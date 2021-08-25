import struct

class pdu():
    def __init__(self,data=None):
        if data is None:
            self.pduData = b''
        else:
            self.pduData = data
    
    def get(self):
        if len(self.pduData) == 0:
            return None
        
        d = self.pduData[0]
        self.pduData = self.pduData[1:]
        return d
        
    def get_data(self, length): 
        if len(self.pduData) < length:
            return None
        d = self.pduData[:length]
        self.pduData = self.pduData[length:]
        return d
    
    def get_all(self):
        d = self.pduData
        #self.pduData = b''
        return d
         
    def get_short(self):
        return struct.unpack('>H',self.get_data(2))[0]

    def get_long(self):
        return struct.unpack('>L',self.get_data(4))[0]

    def put(self, n):
        self.pduData += bytes([n])

    def put_data(self, data):
        self.pduData += data

    def put_short(self, n):
        self.pduData += struct.pack('>H',n & 0xFFFF)

    def put_long(self, n):
        self.pduData += struct.pack('>L',n & 0xFFFFFFFF)

    def length(self):
        return len(self.pduData)


if __name__ == '__main__':
    a = pdu(data=b'\x00\x06')
    b = pdu()
    a.put_short(0x0001)
    a.put_long(0x000B0B02)
    a.put_short(0x0003)
    a.put_short(0x0004)
    p = a.get_short()
    print(hex(p))
    p = a.get_short()
    print(hex(p))
    p = a.get_long()
    print(hex(p))
    p = a.get_long()
    print(p)
    a.put_long(0x0A0B0C0D)
    for i in range(a.length()):        
        p = a.get()
        print(hex(p))
        b.put(p)
    p=b.get_long()
    print(hex(p))
    
