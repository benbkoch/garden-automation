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
            file_object = open('/home/pi/data/data.txt', 'a')
            file_object.write(str(sensorValue) + '\n')
            file_object.close()
    except Exception as e:
        print(e)
    sleep(5)
