#import system libraries
import os
import time, datetime
from time import strftime
from models import Sensors
import RPi.GPIO as GPIO
import Adafruit_MAX31855.MAX31855 as MAX31855


#Variables
roasting_temp = 205.00
roasting_delta = 1.0
heat = 0
cooldown_temp = 25

#NaN tester
def isNaN(num):
    return num != num

#Relay channels setup - BCM pin numbering 
relay_fan    = 17 #Fan power supply (BOARD #11)
relay_heater = 4  #Heater power supply (BOARD# 7)

#Relay is off with HIGH state
relay_off = 1 #GPIO.HIGH
relay_on  = 0 #GPIO.LOW

#Define PIN numbering method
GPIO.setmode(GPIO.BCM)

#Initialize relay channels
GPIO.setup(relay_fan, GPIO.OUT, initial=relay_off)
GPIO.setup(relay_heater, GPIO.OUT, initial=relay_off)


# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)


while (True):
  lsens_temp = sensor.readTempC()
  print lsens_temp
  GPIO.output(relay_heater, relay_on)
  time.sleep(1)
  GPIO.output(relay_heater, relay_off)
  time.sleep(1)
  GPIO.output(relay_fan, relay_on)
  time.sleep(1)
  GPIO.output(relay_fan, relay_off)
  time.sleep(1)
  
  
  
  