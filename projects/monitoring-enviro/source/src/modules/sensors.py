import os
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError, SerialTimeoutError
from enviroplus.noise import Noise
from enviroplus import gas
from subprocess import PIPE, Popen
import logging

class Sensors:
    # BME280 temperature/pressure/humidity sensor
    bme280 = BME280()
    # PMS5003 particulate sensor
    pms5003 = None
    # noise sensor
    noise = Noise()
    # cpu compensation factor
    factor = float(os.environ.get('TEMP_FACTOR', 2.5))
    humi_factor = float(os.environ.get('HUMI_FACTOR', 1.26))
    # storage of cpu temps for smoothing
    cpu_temps = []
    # is the gas sensor attached?
    gas_sensor = False
    values = {}
    def __init__(self, gas_sensor) -> None:
        self.cpu_temps = [self.get_cpu_temperature()] * 10
        self.gas_sensor = gas_sensor
        if (gas_sensor):
            self.pms5003 = PMS5003()


    # Get the temperature of the CPU for compensation
    def get_cpu_temperature(self):
        f = open("/sys/class/thermal/thermal_zone0/temp")
        t = f.read()
        f.close()
        return int(t)/1000.0

    def get_data(self): 
        cpu_temp = self.get_cpu_temperature()
        # Smooth out with some averaging to decrease jitter
        self.cpu_temps = self.cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(self.cpu_temps) / float(len(self.cpu_temps))
        raw_temp = self.bme280.get_temperature()
        adjusted_temp = raw_temp - ((avg_cpu_temp - raw_temp) / self.factor)
        raw_pressure = self.bme280.get_pressure()
        raw_humidity = self.bme280.get_humidity()
        humidity = raw_humidity * self.humi_factor
        
        proximity= ltr559.get_proximity()
        if proximity < 10:
            raw_light = ltr559.get_lux()
        else:
            raw_light = 1

        gas_data = gas.read_all()
        raw_oxidizing = round(gas_data.oxidising/1000, 4)
        raw_reducing = round(gas_data.reducing/1000, 4)
        raw_ammonia = round(gas_data.nh3/1000, 4)
        
        
        raw_1_pm_ug_per_m3 = 0
        raw_25_pm_ug_per_m3 = 0
        raw_10_pm_ug_per_m3 = 0
        if (self.gas_sensor):
            pms_data = None
            try:
                pms_data = self.pms5003.read()
            except (SerialTimeoutError, pmsReadTimeoutError):
                logging.warning("Failed to read PMS5003")
            else:
                raw_1_pm_ug_per_m3 = float(pms_data.pm_ug_per_m3(1.0))
                raw_25_pm_ug_per_m3 = float(pms_data.pm_ug_per_m3(2.5))
                raw_10_pm_ug_per_m3 = float(pms_data.pm_ug_per_m3(10))

        low, mid, high, amp = self.noise.get_noise_profile()
        low *= 128
        mid *= 128
        high *= 128
        amp *= 64

        return {
            "cpu_temp": cpu_temp,
            "proximity": proximity,
            "raw_temperature": round(raw_temp, 4),
            "temperature": round(adjusted_temp, 4),
            "pressure": round(raw_pressure, 4),
            "raw_humidity": round(raw_humidity, 4),
            "humidity": round(humidity, 4),
            "light": raw_light,
            "oxidised": raw_oxidizing,
            "reduced": raw_reducing,
            "nh3": raw_ammonia,

            "pm1": raw_1_pm_ug_per_m3,
            "pm25": raw_25_pm_ug_per_m3,
            "pm10": raw_10_pm_ug_per_m3,

            "noise_low": round(low, 4),
            "noise_mid": round(mid, 4),
            "noise_high": round(high, 4),
            "noise_amplitude": round(amp, 4),
        }