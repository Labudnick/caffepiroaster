# import system libraries
import time
import datetime
import random
from models import DataAccess


class SensorMock:
    def readTempC(self):
        return round(random.uniform(20, 210), 2)


class GPIOMock:
    def output(self, relay_port, relay_state):
        # print "GPIO.output(?, ?)", (relay_port, relay_state)
        return 1


# Relay is off with HIGH state
relay_off = 1  # GPIO.HIGH
relay_on = 0  # GPIO.LOW
# Relay channels setup - BCM pin numbering
relay_fan = 17  # Fan power supply (BOARD #11)
relay_heater = 4  # Heater power supply (BOARD# 7)

# Raspberry Pi related config
try:
    import RPi.GPIO as GPIO
    import Adafruit_MAX31855.MAX31855 as MAX31855

    # Define PIN numbering method
    GPIO.setmode(GPIO.BCM)

    # Initialize relay channels
    GPIO.setup(relay_fan, GPIO.OUT, initial=relay_off)
    GPIO.setup(relay_heater, GPIO.OUT, initial=relay_off)

    # Raspberry Pi software SPI configuration.
    CLK = 25
    CS = 24
    DO = 18
    sensor = MAX31855.MAX31855(CLK, CS, DO)
except:
    sensor = SensorMock()
    GPIO = GPIOMock()


# NaN tester
def isnan(num):
    return num != num


# Variables
roasting_temp = 225.00
roasting_delta = 0
heat = 0
cooldown_temp = 30


def scantempwrite(p_start_time, p_heat, p_roast_status):
    l_sens_temp = sensor.readTempC()
    # Fix temperature reading issues
    while (l_sens_temp == 0) or (isnan(l_sens_temp)):
        time.sleep(0.1)
        l_sens_temp = sensor.readTempC()

    l_process_time = str(datetime.datetime.now() - p_start_time).split('.', 2)[0][2:]
    l_first_crack_time = '00:00'
    if p_roast_status[0] > 1:
        l_first_crack_time = \
        str(datetime.datetime.now() - datetime.datetime.strptime(p_roast_status[4], '%Y-%m-%d %H:%M:%S')).split('.', 2)[
            0][2:]
    DataAccess().insertroastdetails(p_roast_status[3], l_process_time, p_heat, l_sens_temp, p_roast_status[2],
                                    p_roast_status[0], l_first_crack_time)
    return l_sens_temp


print "--->Roasting process started on python side"

# Main loop
while True:
    roastStatus = DataAccess().checkroasting()
    sens_temp = scantempwrite(datetime.datetime.now(), heat, roastStatus)

    if roastStatus[0] > 0:
        # Roast start process flag appeared
        print "--->Innitiate fan"
        GPIO.output(relay_fan, relay_on)
        roasting = 1

        # Roasting with target temperature.
        print "--->Heating starts"
        starttime = datetime.datetime.now()

        while roastStatus[0] > 0:
            if sens_temp > roastStatus[2] + roasting_delta:
                heat = 0
                GPIO.output(relay_heater, relay_off)
            elif sens_temp < roastStatus[2] - roasting_delta:
                heat = 1
                GPIO.output(relay_heater, relay_on)
            time.sleep(1)
            roastStatus = DataAccess().checkroasting()
            sens_temp = scantempwrite(starttime, heat, roastStatus)
        print '--->Cooling down started'
        # Cooling down the roaster to set temperature
        heat = 0

        GPIO.output(relay_heater, relay_off)
        while sens_temp > cooldown_temp:
            time.sleep(1)
            roastStatus = DataAccess().checkroasting()
            sens_temp = scantempwrite(starttime, heat, roastStatus)

        print "--->Cooling down finished"
        GPIO.output(relay_fan, relay_off)
    time.sleep(1)

# if __name__ == "__main__":
#     main()
