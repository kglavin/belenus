from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import os.path
from os import path
import sys

from time import gmtime, strftime
from influxdb import InfluxDBClient

def readDCBattery(modbus_client):
    rr = modbus_client.read_input_registers(address=0, count=4, unit=1)
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


def create_csv():
    datafile = '/home/kevin/sensordata/dcsensor/latest.csv'
    if path.exists(datafile):
        csv = open(datafile, 'a')
    else:
        csv = open(datafile, 'w')
        s = 'datetime,dcv,dci,dcp,dce\n' 
        csv.write(s)
    return csv


def poll_loop(modbus_client,influx_client):
    while True:
        res = dict() 
        data = dict()    
        data['measurement'] = "battery1"    
        data['tags'] = {'id': 'battery'}    
        data['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', gmtime())
        try:
            volts,current,power,energy = readDCBattery(modbus_client)
            res['voltage'] = volts
            res['current'] = current
            res['power'] = power
            res['energy'] = energy
            data['fields'] = res
            measurements = [data]
            try:
                influx_client.write_points(measurements,time_precision='s')
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


if __name__ == '__main__':
    print( 'using port ' ,sys.argv[1])
    #port='/dev/ttyUSB0'
    port = sys.argv[1]
    influxclient = InfluxDBClient('localhost', 8086, 'grafana', 'grafana')
    influxclient.switch_database('batterymon')

    client = ModbusClient(method='rtu', port=port, timeout=1, stopbits = 2, bytesize = 8, parity='N', baudrate= 9600)
    client.connect()

    poll_loop(client,influxclient)