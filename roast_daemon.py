# import system libraries
import os
import time, datetime
import random
from time import strftime
from models import Sensors

# import RPi.GPIO as GPIO
# import Adafruit_MAX31855.MAX31855 as MAX31855


# Variables
roasting_temp = 225.00
roasting_delta = 0
heat = 0
cooldown_temp = 30


# NaN tester
def isNaN(num):
    return num != num


# Relay channels setup - BCM pin numbering
relay_fan = 17  # Fan power supply (BOARD #11)
relay_heater = 4  # Heater power supply (BOARD# 7)

# Relay is off with HIGH state
relay_off = 1  # GPIO.HIGH
relay_on = 0  # GPIO.LOW

# Define PIN numbering method
# GPIO.setmode(GPIO.BCM)

# Initialize relay channels
# GPIO.setup(relay_fan, GPIO.OUT, initial=relay_off)
# GPIO.setup(relay_heater, GPIO.OUT, initial=relay_off)


# Raspberry Pi software SPI configuration.
CLK = 25
CS = 24
DO = 18
# sensor = MAX31855.MAX31855(CLK, CS, DO)


# Roasting stop flag file definition
roast_stop_flag_fname = '.roast_stop_flag'
roast_stop_flag = os.path.dirname(__file__) + '/' + roast_stop_flag_fname


# print roast_stop_flag

class sensor():
    def readTempC(self):
        return round(random.uniform(20, 210), 2)


def ScanTempWrite(starttm, lheat, lroasting):
    lsens_temp = sensor().readTempC()
    # Fix temperature reading issues
    while ((lsens_temp == 0) or (isNaN(lsens_temp))):
        time.sleep(0.1)
        lsens_temp = sensor().readTempC()
    processtime = str(datetime.datetime.utcnow() - starttm).split('.', 2)[0]
    Sensors().InsertData(lsens_temp, processtime, lheat, lroasting)
    return lsens_temp


print "--->Roasting process started on python side"

# Create a flag that prevents roasting from starting
if not os.path.isfile(roast_stop_flag):
    file = open(roast_stop_flag, 'w')
    file.close()

roasting = 0

# Main loop
while True:
    sens_temp = ScanTempWrite(datetime.datetime.utcnow(), heat, roasting)
    if not os.path.isfile(roast_stop_flag):
        # Cleanse database
        Sensors().EraseData()

        # Roast start process flag appeared
        print "--->Innitiate fan"
        # GPIO.output(relay_fan, relay_on)
        time.sleep(1)

        # Roasting with target temperature.
        print "--->Heating starts"
        starttime = datetime.datetime.utcnow()

        while not os.path.isfile(roast_stop_flag):
            roasting = 1
            sens_temp = ScanTempWrite(starttime, heat, roasting)
            if sens_temp > roasting_temp + roasting_delta:
                heat = 0;
                # GPIO.output(relay_heater, relay_off)
            elif sens_temp < roasting_temp - roasting_delta:
                heat = 1
                # GPIO.output(relay_heater, relay_on)
            time.sleep(1)

        print '--->Cooling down started'
        # Cooling down the roaster to set temperature
        heat = 0
        roasting = 0
        # GPIO.output(relay_heater, relay_off)
        sens_temp = ScanTempWrite(starttime, heat, roasting)
        while sens_temp > cooldown_temp:
            time.sleep(1)
            sens_temp = ScanTempWrite(starttime, heat, roasting)
        # GPIO.output(relay_fan, relay_off)
        # GPIO.cleanup()
        print "--->Cooling down finished"

    time.sleep(1)

if __name__ == "__main__":
    main()
