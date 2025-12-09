                                        AIR MOUSE PROJECT
  This is an Arduino project using ESP32 and MPU6050 gyro/accelerometer to make an air mouse. 
It uses the gyro to sense the position of the hand to control the mouse curse on any device.
Window and Android are both supported. 
  Beside bluetooth control, the ESP32 also sends sensor data to InfluxDB for monitoring in Grafana,
and send a Telegram notification when the Air Mouse starts running.

Hardware Used:

  -ESP32
  
  -MPU6050
  
  -Breadboard
  
  -Jumper Wires
  
  -Buttons

Wiring Setup (MPU6050 -> ESP32)

VCC -> 5v

GND -> GND

SDA -> GPIO21

SCL -> GPIO22

Buttons

-button 1 -> GPIO18

-button 2 -> GPIO19


Software & Libraries:

IDE & Tools

  -Arduino IDE
  
Libraries

  -Adafruit MPU6050
  
  -Adafruit sensor
  
  -wire.h
  
  -BLEMOUSE

Features:
  
  - works as a bluetooth air mouse
  
  - real cursor movement using gyro + accel data
  
  - physical buttons for left-click and right-click
  
  - sends motion data to influxDB
  
  - visualizes data on Grafana
  
  - send a Telegram message when the Air mouse starts
  
  - ioT-enable monitoring + notification system

How the System Works

1.  Air Mouse Movement
 
   - ESP32 reads MPU6050 gyro + accel data
   
   - Converts rotation into cursor movement
   
   -  Sends click events through BLE Mouse
     
3. InlfuxDB logging
   
   send the output from Arduino IDE to influxDB
   
5. Grafana visualization
   
   influxDB send the data to grafana.
   
7. Telegram notification
   
   it connected to wifi and send notification to telegram bot.

Authors

-Pang Panhakuntheakreaksmey

-Lou Julie
