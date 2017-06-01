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


def scantempwrite(p_roast_log_id, p_start_time, p_heat, p_roasting, p_temp_set):
    l_sens_temp = sensor.readTempC()
    # Fix temperature reading issues
    while (l_sens_temp == 0) or (isnan(l_sens_temp)):
        time.sleep(0.1)
        l_sens_temp = sensor.readTempC()

    l_process_time = str(datetime.datetime.utcnow() - p_start_time).split('.', 2)[0][2:]
    DataAccess().insertroastdetails(p_roast_log_id, l_process_time, p_heat,  l_sens_temp, p_temp_set, p_roasting)
    return l_sens_temp


print "--->Roasting process started on python side"

roasting = 0

# Main loop
while True:
    sens_temp = scantempwrite('', datetime.datetime.utcnow(), heat, roasting, '')
    roastStatus = DataAccess().checkroasting()
    if roastStatus[0] > 0:
        # Roast start process flag appeared
        print "--->Innitiate fan"
        GPIO.output(relay_fan, relay_on)
        roasting = 1

        # Roasting with target temperature.
        print "--->Heating starts"
        starttime = datetime.datetime.utcnow()

        while roastStatus[0] > 0:

            sens_temp = scantempwrite(roastStatus[3], starttime, heat, roasting, roastStatus[2])
            if sens_temp > roastStatus[1] + roasting_delta:
                heat = 0
                GPIO.output(relay_heater, relay_off)
            elif sens_temp < roastStatus[1] - roasting_delta:
                heat = 1
                GPIO.output(relay_heater, relay_on)
            time.sleep(1)
            roastStatus = DataAccess().checkroasting()

        print '--->Cooling down started'
        # Cooling down the roaster to set temperature
        heat = 0
        roasting = 0

        GPIO.output(relay_heater, relay_off)
        sens_temp = scantempwrite('', starttime, heat, roasting, '')
        while sens_temp > cooldown_temp:
            time.sleep(1)
            sens_temp = scantempwrite('', starttime, heat, roasting, '')

        print "--->Cooling down finished"
        GPIO.output(relay_fan, relay_off)
    time.sleep(1)

# if __name__ == "__main__":
#     main()
