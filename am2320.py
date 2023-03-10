"""
MicroPython Aosong AM2320 I2C driver
https://github.com/mcauser/micropython-am2320
MIT License
Copyright (c) 2016 Mike Causer
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Addendum: Additional changes (c) 2022 Shiraz Billimoria under the same above
license terms
"""

import ustruct
import time

class AM2320:
    
    ERROR_READING=111
    debug=False
    
    def __init__(self, i2c=None, address=0x5c):
        self.i2c = i2c
        self.address = address
        self.buf = bytearray(8)
        self.readinggood = True
    def measure(self):
        buf = self.buf
        address = self.address
        # wake sensor
        if self.debug:
            print("writeto(address, b)")
        try:
            self.i2c.writeto(address, b'')
        except OSError as err:
            if self.debug:
                print(f"writeto (empty) error (continuing): Unexpected {err=}, {type(err)=}")
            pass
        # read 4 registers starting at offset 0x00
        if self.debug:
            print("writeto(address, bx03x00x04)")
        self.i2c.writeto(address, b'\x03\x00\x04')
        # wait at least 1.5ms
        time.sleep_ms(10)
        # read data
        if self.debug:
            print("readfrom_mem_into(address, 0, buf)")
        self.i2c.readfrom_mem_into(address, 0, buf)
        self.readinggood = True
        if self.debug:
            print("unpack")
        crc = ustruct.unpack('<H', bytearray(buf[-2:]))[0]
        if self.debug:
            print("Run CRC")
        if (crc != self.crc16(buf[:-2])):
            # Set readinggood to False
            if self.debug:
                print("crc error detected")
            self.readinggood = False
        return self.readinggood
    def crc16(self, buf):
        crc = 0xFFFF
        for c in buf:
            crc ^= c
            for i in range(8):
                if crc & 0x01:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    def humidity(self):
        if not self.readinggood:
            # Not had a good reading return a predefined value
            return ERROR_READING
        else:
            return (self.buf[2] << 8 | self.buf[3]) * 0.1
    def temperature(self):
        if not self.readinggood:
            # Not had a good reading return a predefined value
            return ERROR_READING
        else:
            t = ((self.buf[4] & 0x7f) << 8 | self.buf[5]) * 0.1
            if self.buf[4] & 0x80:
                t = -t
            return t