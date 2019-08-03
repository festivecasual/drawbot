import time

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)
GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.HIGH)

print('Forward...')

for i in range(300):
    GPIO.output(6, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)
    time.sleep(0.001)
    GPIO.output(6, GPIO.HIGH)
    GPIO.output(24, GPIO.HIGH)

time.sleep(1)

print('Backward...')

GPIO.output(5, GPIO.HIGH)
GPIO.output(23, GPIO.LOW)

time.sleep(1)

for i in range(300):
    GPIO.output(6, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)
    time.sleep(0.001)
    GPIO.output(6, GPIO.HIGH)
    GPIO.output(24, GPIO.HIGH)

GPIO.cleanup()
