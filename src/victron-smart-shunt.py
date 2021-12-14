import time
import os.path
from os import path

from time import gmtime, strftime
from influxdb import InfluxDBClient

import argparse, os, sys
from vedirect import Vedirect

#needed in global context for callback process_solar function to get access to it.
influxclient =  None

def process_solar_all(packet):
    print(len(packet),':',packet)
    if len(packet)>28:
        process_solar(packet)

def process_solar(packet):
    res = dict()
    data = dict()
    data['measurement'] = 'smartshunt1.1'
    data['tags'] = {'id': 'smartshunt'}
    data['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', gmtime())
    try:
    #if True:
        #print(packet)
        volts = int(packet['V'] ) / 1000
        vs = int(packet['VS'] ) / 1000
        current = int(packet['I'] ) / 1000
        power = int(packet['P'])
        soc = int(packet['SOC'] ) / 10
        deepestdischarge = int(packet['H1'] ) / 1000
        lastdischarge = int(packet['H2'] ) / 1000
        avgdischarge = int(packet['H3'] ) / 1000
        chargecycles = int(packet['H4'] ) 
        fulldischarges = int(packet['H5'] ) 
        cumAHdrawn = int(packet['H6'] ) / 1000
        minbattvoltage = int(packet['H7'] ) / 1000
        maxbattvoltage = int(packet['H8'] ) / 1000
        secslastcharge = int(packet['H9'] ) 
        minAuxvoltage = int(packet['H15'] ) / 1000
        maxAuxvoltage = int(packet['H16'] ) / 1000
        dischargedenergy = int(packet['H17'])/100
        chargedenergy = int(packet['H18'])/100

        res['voltage'] = volts 
        res['voltageStarter'] = vs 
        res['current'] = current 
        res['power'] =  power 
        res['soc'] =  soc 
        res['deepestdischarge'] = deepestdischarge
        res['lastdischarge'] = lastdischarge
        res['avgdischarge'] = avgdischarge
        res['fulldischarges'] = fulldischarges
        res['chargecycles'] = chargecycles
        res['cumAHdrawn'] = cumAHdrawn
        res['minbattvoltage'] = minbattvoltage
        res['maxbattvoltage'] = maxbattvoltage
        res['secslastcharge'] = secslastcharge
        res['minAuxvoltage'] = minAuxvoltage
        res['maxAuxvoltage'] = maxAuxvoltage
        res['dischargedenergy'] = dischargedenergy
        res['chargedenergy'] = chargedenergy
        data['fields'] = res
        measurements = [data]


        try:
           influxclient.write_points(measurements,time_precision='s')
        except:
           print('failed to write_points')


        s = time.strftime("%m/%d/%Y %H:%M:%S %z", time.gmtime())+ f',{volts},{current},{power},{chargedenergy},{dischargedenergy},{soc}'    
        print(s)
        s = s +'\n'
    except:
    #else:
        print("Failed to read values")



if __name__ == '__main__':
    print( 'using port ' ,sys.argv[1])
    #port='/dev/ttyUSB1'
    port = sys.argv[1]

    influxclient = InfluxDBClient('localhost', 8086, 'grafana', 'grafana')
    influxclient.switch_database('batterymon')
    storedPacket = None
    while True:
       #try:
       if True:
           ve = Vedirect(port, 30)
           ve.read_data_callback(process_solar_all)
       #except:
       else:
           print(" Failed to vedirect")
