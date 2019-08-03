import time

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    if not GPIO.input(17):
        print('RIGHT is IN')
    if not GPIO.input(27):
        print('LEFT is IN')
    time.sleep(0.5)

GPIO.cleanup()
