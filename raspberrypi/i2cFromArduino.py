#!/usr/bin/env python3
from time import sleep
from smbus2 import SMBusWrapper
address = 0x8

sleep(2)

while 1:
    try:
        with SMBusWrapper(1) as bus:
            data = bus.read_i2c_block_data(address, 99, 2)
            sensorValue = data[0] * 256 + data[1]
            print(sensorValue)
    except:
        print('Oops! Error')
    sleep(5)
