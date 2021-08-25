
import pdu

JDBStart = 0xDD
JDBStop = 0x77 
JDBRead = 0xA5 
JDBWrite = 0x5A
JDBBasicInfo = 0x03
JDBBattCellVoltage = 0x04
JDBProtBoardVer = 0x05
JDBReadOk = 0x00
JDBReadError = 0x80
JDBNull = 0xff

class JDB():
    def __init__(self):
        self.pdu = pdu.pdu()
        self.check_accumulator = 0x00
        
    def push_with_checksum(self,b):
        self.pdu.put(b)
        self.check_accumulator = (self.check_accumulator + b) & 0xFF
    
    def add_checksum(self):
        c = 0x10000 - self.check_accumulator
        msb = (c >> 8) & 0xFF
        lsb = c & 0xFF
        self.pdu.put(msb)
        self.pdu.put(lsb)

    def read_basic_info(self):
        self.pdu.put(JDBStart)
        self.pdu.put(JDBRead)
        self.push_with_checksum(JDBBasicInfo)
        #length = 0
        self.push_with_checksum(0)
        #self.push_with_checksum(JDBNull)
        self.add_checksum()
        self.pdu.put(JDBStop)

    def read_battery_cell(self):
        self.pdu.put(JDBStart)
        self.pdu.put(JDBRead)
        self.push_with_checksum(JDBBattCellVoltage)
        #length = 0
        self.push_with_checksum(0)
        #self.push_with_checksum(JDBNull)
        self.add_checksum()
        self.pdu.put(JDBStop)    
        
    def read_protection_info(self):
        self.pdu.put(JDBStart)
        self.pdu.put(JDBRead)
        self.push_with_checksum(JDBProtBoardVer)
        #length = 0
        self.push_with_checksum(0)
        #self.push_with_checksum(JDBNull)
        self.add_checksum()
        self.pdu.put(JDBStop)

    def get(self):
        return self.pdu.get_all()

class JDBResponse():
    def __init__(self,rxdata):
        # validity of the received and parsed data
        self.validPDU = True
        self.pdu = pdu.pdu(rxdata)
        #protocol parsings kept for debug/check
        self.response_code = 0
        self.length = 0
        self.data = None
        self.rxstatus = 0
        self.rx_checksum = 0
        self.checksum = 0
        self.resp = {}
        checksum_accumulator = 0x0000

        # assure that we received some data to start
        if self.pdu.length() == 0:
            self.validPDU = False
            return
        
        #check start byte
        b = self.pdu.get()
        if b != JDBStart:
            self.validPDU = False
            return

        # check response code is one of the valid types
        self.response_code = self.pdu.get()
        if self.response_code not in [JDBBasicInfo,JDBBattCellVoltage,JDBProtBoardVer ]:
            self.validPDU = False
            return
        else:
            self.resp['type'] = self.response_code
        
        #check rx status byte to see did the requested operation sucees
        self.rxstatus = self.pdu.get()
        if  self.rxstatus == JDBReadError:
            self.validPDU = False
            self.resp['error'] = self.rxstatus
            return 
        if self.rxstatus == JDBReadOk:
            self.validPDU = True
            self.resp['error'] = self.rxstatus
            checksum_accumulator += self.rxstatus
   

        #length of data embedded in pdu
        self.length = self.pdu.get()
        if self.length == 0:
            self.validPDU = False
            return
        else:
            checksum_accumulator += self.length
            self.validPDU = True

        #data
        self.data = self.pdu.get_data(self.length)

        # received checksim, recalculate based on received data and validate received pdu
        self.rx_checksum = self.pdu.get_short()
        for i in range(self.length):
            checksum_accumulator += self.data[i]
        checksum = 0x10000 - checksum_accumulator

        if checksum == self.rx_checksum: 
            self.validPDU = True
        else:
            self.validPDU = False
            return

        # validate reception of stop byte
        b = self.pdu.get()
        if b != JDBStop:
            self.validPDU = False
            return 

        self.validPDU = True
        #parse data into dict based on type
        if self.response_code == JDBBasicInfo:
            self._parse_basic_info()
        #return ok
        return

    def _parse_basic_info(self):
        p = pdu.pdu(self.data)
        voltage = p.get_short()
        self.resp['voltage'] = voltage/100

        #parse as signed 16bits
        c = p.get_short()
        current = -(c & 0x8000) | (c & 0x7fff)

        self.resp['current'] = current/100
        if current > 0:
            self.resp['charging'] = True
        else:
            self.resp['charging'] = False

        balance_capacity = p.get_short()
        self.resp['balance_capacity'] = balance_capacity/100

        rate_capacity = p.get_short()
        self.resp['rate_capacity'] = rate_capacity/100

        cycle = p.get_short()
        self.resp['cycle'] = cycle

        production_date = p.get_short()
        self.resp['production_date'] = production_date

        balance_status = p.get_short()
        self.resp['balance_status'] = balance_status

        balance_status_high = p.get_short()
        self.resp['balance_status_high'] = balance_status_high


        protection_status = p.get_short()
        self.resp['protection_status'] = protection_status

        sw_version = p.get()
        self.resp['sw_version'] = sw_version

        remaining_soc = p.get()
        self.resp['remaining_soc'] = remaining_soc

        fet_status  = p.get()
        self.resp['fet_status'] = fet_status

        battery_series = p.get()
        self.resp['battery_series'] = battery_series
        ntc_number = p.get()
        self.resp['ntc_number'] = ntc_number
        ntc = []
        for i in range(ntc_number):
            ntc.append(p.get_short())
            n = 'ntc_'+str(i)
            self.resp[n] = (ntc[i] -2731)/10
        return


def unit_test():
    r = JDB()
    r.read_basic_info()
    print(r.get())
    r = JDB()
    r.read_battery_cell()
    print(r.get())
    r = JDB()
    r.read_protection_info()
    print(r.get())

    response_data1 = b'\xDD\x03\x00\x1B\x17\x00\x00\x00\x02\xD0\x03'
    response_data2 = b'\xE8\x00\x00\x20\x78\x00\x00\x00\x00\x00\x00\x10\x48\x03\x0F\x02\x0B\x76\x0B\x82\xFB\xFF\x77'
    resp =  JDBResponse(response_data1 + response_data2)


if __name__ == '__main__':
    unit_test()

