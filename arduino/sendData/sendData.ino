/*
  Arduino Slave for Raspberry Pi Master
  i2c_slave_ard.ino
  Connects to Raspberry Pi via I2C
  
  DroneBot Workshop 2019
  https://dronebotworkshop.com
*/
 
// Include the Wire library for I2C
#include <Wire.h>

// LED on pin 13
const int ledPin = 13; 
const int sensorPin = A6;

int sensorValue = 0;
 
void setup() {
  // Join I2C bus as slave with address 8
  Serial.begin(9600);
  Wire.begin(0x8);

  
  // Setup pin 13 as output and turn LED off
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  Wire.onRequest(sendData);
}

void sendData() {
  sensorValue = analogRead(sensorPin);
  Serial.println(sensorValue);
  uint8_t buffer[2];
  buffer[0] = sensorValue >> 8;
  buffer[1] = sensorValue & 0xff;
  Wire.write(buffer, 2);
}
 
void loop() {
}
