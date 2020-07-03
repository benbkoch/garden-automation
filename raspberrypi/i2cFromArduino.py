#!/usr/bin/env python3
from time import sleep
import time
import argparse
import json
from smbus2 import SMBusWrapper
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient


address = 0x8

sleep(2)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    return args

def readIntFromI2C():
    with SMBusWrapper(1) as bus:
        data = bus.read_i2c_block_data(address, 99, 2)
        sensorValue = data[0] * 256 + data[1]
        return sensorValue

def writeValuesToFile(values, filename):
    file_object = open(filename, 'a')
    strings = [str(value) for value in values]
    timestamp = str(time.time())
    file_object.write(timestamp + "," + ",".join(strings) + '\n')
    file_object.close()

def waterSensorRawToPercentage(value):
    voltage = value * (3.3 / 1024)
    print(voltage)

    soilMoisturePercentage = 0
    if voltage < 1.1:
        soilMoisturePercentage = (10 * voltage) - 1
    elif voltage < 1.3:
        soilMoisturePercentage = (25 * voltage) - 17.5
    elif voltage < 1.82:
        soilMoisturePercentage = (48.08 * voltage) - 47.5
    elif voltage < 2.2:
        soilMoisturePercentage = (26.32 * voltage) - 7.89
    else:
        soilMoisturePercentage = (62.5 * voltage) - 87.5
    return soilMoisturePercentage

# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("moisture: " + str(payloadDict["state"]["reported"]["moisturePercentage"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def writeSensorValuesToShadow(rawSensorValue, sensorPercentage, handler):
    timestamp = str(time.time())
    payload = {"state": {"reported": {"moistureRaw": str(rawSensorValue), "moisturePercentage": sensorPercentage, "timestamp": timestamp}}}
    handler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)


args = parseArgs()

if not args.port:
    args.port = 8883

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(args.clientId)
myAWSIoTMQTTShadowClient.configureEndpoint(args.host, args.port)
myAWSIoTMQTTShadowClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)

# AWSIoTMQTTShadowClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5) # 5 sec

myAWSIoTMQTTShadowClient.connect()

deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(args.thingName, True)

while 1:
    try:
        sensorValue = readIntFromI2C()
        percentage = waterSensorRawToPercentage(sensorValue)
        writeValuesToFile([sensorValue, percentage], '/home/pi/data/data.txt')

        writeSensorValuesToShadow(sensorValue, percentage, deviceShadowHandler)
    except Exception as e:
        print(e)
    sleep(60)


