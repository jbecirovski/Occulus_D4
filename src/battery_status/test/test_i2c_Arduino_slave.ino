/*
  Arduino Slave for Raspberry Pi Master
  i2c_slave_ard.ino
  Connects to Raspberry Pi via I2C
  
  2021
*/
 
// Include the Wire library for I2C
#include <Wire.h>
 
// LED on pin 13
const int ledPin = 13; 
int c = 0;
uint8_t data[3];
uint8_t command = 0x00;
uint8_t test = 0x00;
 
void setup() {
  // Join I2C bus as slave with address 8
  Wire.begin(0x0B);
  
  // Call receiveEvent when data received                
  Wire.onReceive(receiveEvent);

  // Call receiveEvent when data received                
  Wire.onRequest(requestEvent);

  Serial.begin(9600);
  
  // Setup pin 13 as output and turn LED off
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, c);
  Serial.print("Ready! \n");
}
 
// Function that executes whenever data is received from master
void receiveEvent(int howMany) {
  while (Wire.available()) { // loop through all but the last
    command = Wire.read();
    Serial.print("command:");
    Serial.print(command);
    Serial.print("\n");
    data[0] = Wire.read();
    if (data[0] != 255)
    {
      data[1] = Wire.read();
      data[2] = Wire.read();
      Serial.print("Data received:");
      Serial.print("LSB:");
      Serial.print(data[0]);
      Serial.print(", MSB:");
      Serial.print(data[1]);
      Serial.print(" and CRC:");
      Serial.print(data[2]);    
      Serial.print("\n");
    }
  }
}
// Function that executes whenever data is request from master
void requestEvent() {
  if (command == 0x09)
    {
      data[0] = 0xC2;
      data[1] = 0x0E;
      data[2] = 0x86;
    }
  Wire.write(data, 3);
  Serial.print("Data send:");
  Serial.print("LSB:");
  Serial.print(data[0]);
  Serial.print(", MSB:");
  Serial.print(data[1]);
  Serial.print(" and CRC:");
  Serial.print(data[2]);    
  Serial.print("\n");
  c = c ^ 1;
  digitalWrite(LED_BUILTIN, c);
}
void loop() {
  delay(100);
}
