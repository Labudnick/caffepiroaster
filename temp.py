#import datetime
import time
from time import strftime
from models import Sensors

#import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855


# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)

def isNaN(num):
    return num != num

# Loop printing measurements every second.
while True:
    sens_temp = sensor.readTempC()
    if (( sens_temp == 0) or (isNaN(sens_temp))):
	time.sleep(1)
	sens_temp = sensor.readTempC()
	
    datetime=strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    Sensors().InsertData(sens_temp, datetime)
    print sens_temp, datetime
    time.sleep(1)
