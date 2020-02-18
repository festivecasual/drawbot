import time
from math import sqrt
import re

import RPi.GPIO as GPIO
import pigpio


GPIO.setmode(GPIO.BCM)


# Init Stepper Control

GPIO.setup(20, GPIO.OUT)    # Right pulse
GPIO.setup(21, GPIO.OUT)    # Right direction
GPIO.setup(23, GPIO.OUT)    # Left pulse
GPIO.setup(24, GPIO.OUT)    # Left direction

GPIO.output(20, GPIO.HIGH)  # Init right pulse
GPIO.output(21, GPIO.HIGH)  # Set right to outfeed
GPIO.output(23, GPIO.HIGH)  # Init left pulse
GPIO.output(24, GPIO.LOW)   # Set left to outfeed


# Stepper Pulse

def pulse(channel, times=1):
    while times:
        GPIO.output(channel, GPIO.LOW)
        time.sleep(0.005)
        GPIO.output(channel, GPIO.HIGH)
        times -= 1

print('Right Stepper (Outfeed)...')
pulse(20, 100)

time.sleep(1)

print('Left Stepper (Outfeed)...')
pulse(23, 100)

GPIO.cleanup()
