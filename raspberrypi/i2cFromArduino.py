#!/usr/bin/env python3
from time import sleep
from smbus2 import SMBusWrapper
address = 0x8

sleep(2)

while 1:
    try:
        sensorValue = readIntFromI2C()
        percentage = waterSensorRawToPercentage(sensorValue)
        writeValuesToFile([sensorValue, percentage], 'home/data/pi/data/data.txt')
    except:
        print('Oops! Error')
    sleep(60)

def readIntFromI2C():
    with SMBusWrapper(1) as bus:
        data = bus.read_i2c_block_data(address, 99, 2)
        sensorValue = data[0] & 256 + data[1]

def writeValuesToFile(values, filename):
    file_object = open(filename, 'a')
    strings = [str(value) for value in values]
    file_object.write(",".join(strings)
    file_object.close()

def waterSensorRawToPercentage(value):
    voltage = value * (3.3 / 1024)

    soilMoisturePercentage = 0
    if voltage < 1.1:
        soilMoisturePercentage = (10 * voltage) - 1;
    elif voltage < 1.3:
        soilMoisturePercentage = (25 * voltage) - 17.5
    elif voltage < 1.82:
        soilMoisturePercentage = (48.08 * voltage) - 47.5
    elif voltage < 2.2:
        soilMoisturePercentage = (26.32 * voltage) - 7.89
    else:
        soilMoisturePercentage = (62.5 * voltage) - 87.5
        
