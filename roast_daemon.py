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
roasting_temp = float(DataAccess().get_param_by_name('roast_temp_max')[0])
roasting_delta = 0
heat = 0
cooldown_temp = float(DataAccess().get_param_by_name('cooldown_temp')[0])
cooldown = 0

def scantempwrite(p_heat, p_roast_status):
    l_sens_temp = round(sensor.readTempC(),0)
    # Fix temperature reading issues
    while (l_sens_temp == 0) or (isnan(l_sens_temp)):
        time.sleep(0.1)
        l_sens_temp = sensor.readTempC()
    DataAccess().insert_roast_details(p_roast_status[3], p_heat, l_sens_temp, p_roast_status[2],
                                    p_roast_status[0])
    return l_sens_temp


print "--->Roasting process started on python side"

# Main loop
while True:
    roastStatus = DataAccess().check_roasting()
    sens_temp = scantempwrite(heat, roastStatus)

    if roastStatus[0] > 0:
        # Roast start process flag appeared
        print "--->Innitiate fan"
        GPIO.output(relay_fan, relay_on)
        roasting = 1

        # Roasting with target temperature.
        print "--->Heating starts"
        # nieuzywane ? starttime = datetime.datetime.now()

        while roastStatus[0] > 0 and cooldown == 0:
            if sens_temp > roastStatus[2] + roasting_delta:
                heat = 0
                GPIO.output(relay_heater, relay_off)
            elif sens_temp < roastStatus[2] - roasting_delta:
                heat = 1
                GPIO.output(relay_heater, relay_on)
            time.sleep(1)
            roastStatus = DataAccess().check_roasting()
            sens_temp = scantempwrite(heat, roastStatus)
            # If after 1st crack time is up, end the process
            if roastStatus[5] >= roastStatus[4]:
                DataAccess().end_roasting(roastStatus[3])
                cooldown = 1;
        print '--->Cooling down started'
        # Cooling down the roaster to set temperature
        heat = 0

        GPIO.output(relay_heater, relay_off)

        print (type(cooldown_temp))

        while sens_temp > cooldown_temp:
            time.sleep(1)
            roastStatus = DataAccess().check_roasting()
            sens_temp = scantempwrite(heat, roastStatus)

        print "--->Cooling down finished"
        GPIO.output(relay_fan, relay_off)
        cooldown = 0
    time.sleep(1)

# if __name__ == "__main__":
#     main()
