#Load GPIO board module
try:
	import RPi.GPIO as GPIO
	import time
except RunTimeError:
	print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


#Relay channels setup - pin numbering 
relay_l1 = 11 #Fan power supply
relay_l2 = 7  #channel2 =  #Heater power supply

#Relay is off with HIGH state
relay_off = GPIO.HIGH
relay_on  = GPIO.LOW

#Define PIN numbering method
GPIO.setmode(GPIO.BOARD)

#Initialize relay channels
GPIO.setup(relay_l1, GPIO.OUT, initial=relay_off)
GPIO.setup(relay_l2, GPIO.OUT, initial=relay_off)

time.sleep(5)

GPIO.output(relay_l1, relay_on)
time.sleep(1)
GPIO.output(relay_l2, relay_on)
time.sleep(3)
GPIO.output(relay_l1, relay_off)
time.sleep(1.5)
GPIO.output(relay_l2, relay_off)
time.sleep(1)
GPIO.cleanup()
