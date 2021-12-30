import time
import os.path
from os import path

from time import gmtime, strftime
from influxdb import InfluxDBClient

import argparse, os, sys
from vedirect import Vedirect

#needed in global context for callback process_solar function to get access to it.
influxclient =  None
solarid='solar'

def process_solar(packet):
    res = dict()
    data = dict()
    data['measurement'] = 'solar1.3'
    data['tags'] = {'id': solarid}
    data['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', gmtime())
    try:
        volts = int(packet['V'] ) / 1000
        current = int(packet['I'] ) / 1000
        power = volts * current 
        energy = 0 
        panelvolts = int(packet['VPV'])/1000
        panelpower = int(packet['PPV'])
        yieldtotal = int(packet['H19'])/100
        yieldtoday = int(packet['H20'])/100
        maxpowertoday = int(packet['H21'])
        yieldyesterday = int(packet['H22'])/100
        maxpoweryesterday = int(packet['H23'])

        res['voltage'] = volts 
        res['current'] = current 
        res['power'] =  power 
        res['energy'] = energy
        res['panelvoltage'] = panelvolts
        res['panelpower'] = panelpower
        res['yieldtotal'] = yieldtotal
        res['yieldtoday'] = yieldtoday
        res['maxpowertoday'] = maxpowertoday
        res['yieldyesterday'] = yieldyesterday
        res['maxpoweryesterday'] = maxpoweryesterday
        data['fields'] = res
        measurements = [data]
        try:
           influxclient.write_points(measurements,time_precision='s')
        except:
            print('failed to write_points')


        s = time.strftime("%m/%d/%Y %H:%M:%S %z", time.gmtime())+ f',{volts},{current},{power},{energy},{panelvolts},{panelpower}'    
        s = s + f',{yieldtotal},{yieldtoday},{maxpowertoday},{yieldyesterday},{maxpoweryesterday}'
        print(s)
        s = s +'\n'
    except:
    #else:
        print("Failed to read values")



if __name__ == '__main__':
    print( 'using port ' ,sys.argv[1])
    #port='/dev/ttyUSB1'
    solarid = sys.argv[1]
    port = sys.argv[2]

    influxclient = InfluxDBClient('localhost', 8086, 'grafana', 'grafana')
    influxclient.switch_database('batterymon')

    while True:
       try:
           ve = Vedirect(port, 30)
           ve.read_data_callback(process_solar)
       except:
           print(" Failed to vedirect")
