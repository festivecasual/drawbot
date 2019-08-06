import time
from math import sqrt, floor

import RPi.GPIO as GPIO
import pigpio


GPIO.setmode(GPIO.BCM)


# Init Stepper Control

GPIO.setup(5, GPIO.OUT)     # Left Direction
GPIO.setup(6, GPIO.OUT)     # Left Pulse
GPIO.setup(23, GPIO.OUT)    # Right Direction
GPIO.setup(24, GPIO.OUT)    # Right Pulse

GPIO.output(6, GPIO.HIGH)   # Init left pulse
GPIO.output(24, GPIO.HIGH)  # Init right pulse
GPIO.output(5, GPIO.LOW)    # Set left to outfeed
GPIO.output(23, GPIO.HIGH)  # Set right to outfeed


# Stepper Pulse

def pulse(channel, times=1):
    while times:
        GPIO.output(channel, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(channel, GPIO.HIGH)
        times -= 1


# Movement Control

MAX_LEFT = 559    # Feedout of left belt to end stop (mm)
MAX_RIGHT = 538   # Feedout of right belt to end stop (mm)
L = 523           # Horizontal pitch between steppers (mm)
# STEP = 49 / 500   # Step size (mm)
STEP = 12 * 3.14159 / 400   # Step size (mm)

def move_to(x, y, left, right):
    tgt_left = sqrt(x**2 + y**2)
    tgt_right = sqrt((L - x)**2 + y**2)

    if tgt_left > left:
        GPIO.output(5, GPIO.LOW)
    else:
        GPIO.output(5, GPIO.HIGH)

    if tgt_right > right:
        GPIO.output(23, GPIO.HIGH)
    else:
        GPIO.output(23, GPIO.LOW)

    left_steps = int(abs(tgt_left - left) / STEP)
    right_steps = int(abs(tgt_right - right) / STEP)
    slope = right_steps / left_steps

    # Pulse each left_step one at a time
    # Pulse 1+ right_steps when the slope of the movement merits it
    right_counter = 0
    for i in range(1, left_steps + 1):
        pulse(6)
        left_steps -= 1

        right_counter += slope
        if int(right_counter):
            pulse(24, int(right_counter))
            right_steps -= int(right_counter)

            right_counter = right_counter % 1

    # Pulse any remaining right_steps from rounding or the special
    # case of left_steps = 0
    pulse(24, right_steps)

    return (tgt_left, tgt_right)


# Init Limit Switches

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Left Limit
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Right Limit


# Init Servo (Pen Lifter) Control

pi = pigpio.pi()

PEN_DOWN = 60000
PEN_UP = 110000

def pen_up():
    global pen
    pen = PEN_UP
    pi.hardware_PWM(18, 50, pen)

def pen_down():
    global pen
    while pen > PEN_DOWN:
        pen -= 100
        pi.hardware_PWM(18, 50, pen)
        time.sleep(0.01 / (PEN_UP / pen) ** 1.5)

pen = PEN_UP


# Centering Routine

def center():
    while True:
        if not GPIO.input(27):
            break
        pulse(6)

    GPIO.output(5, GPIO.HIGH)
    pulse(6, 2000)
    GPIO.output(5, GPIO.LOW)

    left = MAX_LEFT - 2000 * STEP

    while True:
        if not GPIO.input(17):
            break
        pulse(24)

    GPIO.output(23, GPIO.LOW)
    pulse(24, 2000)
    GPIO.output(23, GPIO.HIGH)

    right = MAX_RIGHT - 2000 * STEP

    origin_x = (left**2 - right**2 + L**2) / (2 * L)
    origin_y = sqrt(left**2 - origin_x**2)
    return left, right, origin_x, origin_y


# Startup

pen_up()
left, right, origin_x, origin_y = center()


# Test drawing

pen_down()

left, right = move_to(origin_x + 0, origin_y + 50, left, right)
left, right = move_to(origin_x + 50, origin_y + 50, left, right)
left, right = move_to(origin_x + 50, origin_y + 0, left, right)
left, right = move_to(origin_x + 0, origin_y + 0, left, right)

pen_up()


# Finalization

GPIO.cleanup()
