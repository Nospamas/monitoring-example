from functools import reduce
from collections import defaultdict




class Smoother:

    def __init__(self, telegraf_interval, inner_interval):
        self.telegraf_interval = telegraf_interval
        self.data_points = telegraf_interval/inner_interval
        self.data = []

    def add(self, data):
        self.data.append(data)
        if (len(self.data) > self.data_points):
            self.data.pop(0)

    def get_period_average(self):
        alldata = defaultdict(list)

        for i in self.data:
            for k, v in i.items():
                alldata[k].append(v)
        
        avgData = {}
        
        for k,v in alldata.items():
            avgData[k] = round(sum(v) / len(v), 4)
        
        return avgData