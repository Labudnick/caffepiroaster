import datetime
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855


# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)

# Loop printing measurements every second.
temp = sensor.readTempC()
now = datetime.datetime.now()
print(now.strftime('%Y-%m-%d %H:%M:%S') + ',{0:0.2F}'.format(temp))

