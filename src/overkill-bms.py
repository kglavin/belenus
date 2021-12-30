
import sys
import time
from time import gmtime, strftime,sleep
from influxdb import InfluxDBClient
import serial
from JDB_proto import JDB, JDBResponse

bmsid = 'bms-1'

def poll_loop(client,influx_client):
    while True:
        sleep(4)
        try:
            r = JDB()
            r.read_basic_info()
            d = r.get()
            client.write(d) 
            data = dict()    
            data['measurement'] = "bms-0.1"    
            data['tags'] = {'id': bmsid}    
            data['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', gmtime())
            try:
                sleep(1)
                serialdata = client.read(100)
                r = JDBResponse(serialdata)
                if r.validPDU == True:
                    data['fields'] = r.resp
                    measurements = [data]
                    try:
                        influx_client.write_points(measurements,time_precision='s')
                        pass
                    except:
                        print('failed to write_points')
                s = time.strftime("%m/%d/%Y %H:%M:%S %z", time.gmtime()) +' : '+ str(r.resp['voltage']) + ', '+str(r.resp['current']) +', '+str(r.resp['ntc_0']) +', '+str(r.resp['remaining_soc'])+', '+str(r.resp['charging'])+', '+str(r.resp['rate_capacity'])
                print(s)
            except:
                print("Failed to read values")
                sleep(15)
        except:
                print('failed to sent request')
                sleep(20)
                
class client():
    def __init__(self):
        pass

    def write(self,data):
        print('wrote: ', data)

    def read(self,n):
        response_data1 = b'\xDD\x03\x00\x1B\x17\x00\x00\x00\x02\xD0\x03'
        response_data2 = b'\xE8\x00\x00\x20\x78\x00\x00\x00\x00\x00\x00\x10\x48\x03\x0F\x02\x0B\x76\x0B\x82\xFB\xFF\x77'
        return response_data1 + response_data2


if __name__ == '__main__':
    #print( 'using port ' ,sys.argv[1])
    #port='/dev/ttyUSB1'
    port = sys.argv[1]
    bmsid = sys.argv[2]

    influxclient = InfluxDBClient('localhost', 8086, 'grafana', 'grafana')
    influxclient.switch_database('batterymon')
    client = serial.Serial(port, 9600, timeout=1)
    #influxclient = 1
    #client = client()

    poll_loop(client,influxclient)
