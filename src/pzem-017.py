from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import os.path
from os import path

from time import gmtime, strftime
from influxdb import InfluxDBClient


influxclient = InfluxDBClient('localhost', 8086, 'grafana', 'grafana')
influxclient.switch_database('batterymon')



client = ModbusClient(method='rtu', port='/dev/ttyUSB0', timeout=1, stopbits = 2, bytesize = 8, parity='N', baudrate= 9600)
client.connect()

def readDCBattery():
    rr = client.read_input_registers(address=0, count=4, unit=1)
    volts=rr.getRegister(0)/100.00
    current= rr.getRegister(1) /100.0
    power_lsw= rr.getRegister(2)/10 
    power_hsw= rr.getRegister(3) 
    power = (power_hsw * 2**16) + power_lsw
    #energy_lsw= rr.getRegister(4) 
    #energy_hsw= rr.getRegister(5) 
    #energy = (energy_hsw * 2**16) + energy_lsw
    energy=1
    return(volts,current,power,energy)


datafile = '/home/kevin/sensordata/dcsensor/latest.csv'
if path.exists(datafile):
    csv = open(datafile, 'a')
else:
    csv = open(datafile, 'w')
    s = 'datetime,dcv,dci,dcp,dce\n' 
    csv.write(s)


while True:
    res = dict() 
    data = dict()    
    data['measurement'] = "battery1"    
    data['tags'] = {'id': 'battery'}    
    data['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', gmtime())
    try:
        volts,current,power,energy = readDCBattery()

        res['voltage'] = volts
        res['current'] = current
        res['power'] = power
        res['energy'] = energy
        data['fields'] = res
        measurements = [data]
        try:
           influxclient.write_points(measurements,time_precision='s')
        except:
            print('failed to write_points')


        s = time.strftime("%m/%d/%Y %H:%M:%S %z", time.gmtime())+","+str(volts)+"," + str(current) + ","+str(power) +","+str(energy)
        print(s)
        s = s +'\n'
        #csv.write(s)
        #csv.flush()
        time.sleep(5)
    except:
        print("Failed to read values")
        time.sleep(20)
