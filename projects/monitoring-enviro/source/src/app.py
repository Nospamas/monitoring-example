from modules.sensors import Sensors
import logging
import time
from modules.smoother import Smoother
import threading
from flask import Flask, render_template, url_for, request
import os

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

run_flag = True


telegraf_polling_interval = float(os.environ.get('TELEGRAF_INTERVAL', 1.26))
host_port = int(os.environ.get('HOST_PORT', 8091))
gas_sensor = os.environ.get('GAS_SENSOR', 'false').lower() == 'true'
inner_polling_interval = 0.5

sensors = Sensors(gas_sensor)
smoother = Smoother(telegraf_polling_interval, inner_polling_interval)
smoother.add(sensors.get_data())


def background():
    global record, data
    while run_flag:
        data = sensors.get_data()
        logging.info("inner: " + data.__str__())
        smoother.add(data)
        time.sleep(inner_polling_interval)
        

background_thread = threading.Thread(target = background)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
log = logging.getLogger("werkzeug")
log.disabled = True

@app.route('/average')
def average():
    return smoother.get_period_average()
if __name__ == '__main__':
    background_thread.start()
    try:
        app.run(debug = False, host = '0.0.0.0', port = host_port, use_reloader = False)
    except Exception as e:
        print(e)
        pass
    run_flag = False
    print("Waiting for background to quit")
    background_thread.join()
