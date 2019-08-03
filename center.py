import time

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.OUT)     # Left Direction
GPIO.setup(6, GPIO.OUT)     # Left Pulse
GPIO.setup(23, GPIO.OUT)    # Right Direction
GPIO.setup(24, GPIO.OUT)    # Right Pulse

GPIO.output(6, GPIO.HIGH)   # Left Pulse Init
GPIO.output(24, GPIO.HIGH)  # Right Pulse Init
GPIO.output(5, GPIO.LOW)    # Left Set to Outfeed
GPIO.output(23, GPIO.HIGH)  # Right Set to Outfeed


def pulse(channel):
    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.001)
    GPIO.output(channel, GPIO.HIGH)


GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Left Limit
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Right Limit


while True:
    if not GPIO.input(27):
        break
    pulse(6)
    time.sleep(0.001)

GPIO.output(5, GPIO.HIGH)
for i in range(2000):
    pulse(6)
    time.sleep(0.001)
GPIO.output(5, GPIO.LOW)

while True:
    if not GPIO.input(17):
        break
    pulse(24)
    time.sleep(0.001)

GPIO.output(23, GPIO.LOW)
for i in range(2000):
    pulse(24)
    time.sleep(0.001)
GPIO.output(23, GPIO.HIGH)


GPIO.cleanup()
