import time

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)

def pulse(pin, times=1):
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.005)
    GPIO.output(pin, GPIO.HIGH)

    times -= 1
    if times:
        pulse(pin, times)


pulse(6, 500)

GPIO.cleanup()
