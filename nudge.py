import time

import RPi.GPIO as GPIO
from getch import getch


GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)
GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.HIGH)

print('Press d/f and j/k to operate left and right steppers.')
print('Press <enter> to confirm center.')

def pulse(pin, times=1):
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.005)
    GPIO.output(pin, GPIO.HIGH)

    times -= 1
    if times:
        pulse(pin, times)

ch = getch()
while ch != '\n':
    if ch == 'd':
        GPIO.output(5, GPIO.HIGH)
        pulse(6, 5)
    elif ch == 'f':
        GPIO.output(5, GPIO.LOW)
        pulse(6, 5)
    elif ch == 'j':
        GPIO.output(23, GPIO.HIGH)
        pulse(24, 5)
    elif ch == 'k':
        GPIO.output(23, GPIO.LOW)
        pulse(24, 5)
    ch = getch()

GPIO.cleanup()
