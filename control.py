import time
from math import sqrt
import re

import RPi.GPIO as GPIO
import pigpio


# GPIO: Stepper control
RIGHT_PULSE = 20
RIGHT_DIRECTION = 21
LEFT_PULSE = 23
LEFT_DIRECTION = 24

# GPIO: Limit switches
LEFT_LIMIT = 17
RIGHT_LIMIT = 27

# GPIO: Servo PWM wire (pen lifter)
PWM = 18

# Machine parameters
MAX_LEFT = 513              # Feedout of left belt to end stop (mm)
MAX_RIGHT = 516             # Feedout of right belt to end stop (mm)
L = 523                     # Horizontal pitch between steppers (mm)
STEP = 12 * 3.14159 / 200   # Step size (mm)
PAUSE = 0.005               # Time to wait between movements (s)
PEN_EXTENT = 0.5            # Lift ratio for pen raises
PEN_DOWN = 20000            # Pen down servo position
PEN_UP = 80000              # Pen up servo position


# Stepper actions

def pulse(channel, times=1):
    while times > 0:
        GPIO.output(channel, GPIO.LOW)
        time.sleep(PAUSE)
        GPIO.output(channel, GPIO.HIGH)
        times -= 1

def move_to(x, y, left, right):
    tgt_left = sqrt(x**2 + y**2)
    tgt_right = sqrt((L - x)**2 + y**2)

    # Catch no-op special case
    if tgt_left == left and tgt_right == right:
        return (tgt_left, tgt_right)

    if tgt_left >= left:
        GPIO.output(LEFT_DIRECTION, GPIO.LOW)
        left_direction = 1
    else:
        GPIO.output(LEFT_DIRECTION, GPIO.HIGH)
        left_direction = -1

    if tgt_right >= right:
        GPIO.output(RIGHT_DIRECTION, GPIO.HIGH)
        right_direction = 1
    else:
        GPIO.output(RIGHT_DIRECTION, GPIO.LOW)
        right_direction = -1

    left_steps = int(abs(tgt_left - left) / STEP)
    right_steps = int(abs(tgt_right - right) / STEP)
    slope = right_steps / left_steps if left_steps > 0 else 0

    act_left = left + left_direction * left_steps * STEP
    act_right = right + right_direction * right_steps * STEP

    # Pulse each left_step one at a time
    # Pulse 1+ right_steps when the slope of the movement merits it
    right_counter = 0
    for i in range(1, left_steps + 1):
        pulse(LEFT_PULSE)
        left_steps -= 1

        right_counter += slope
        if int(right_counter):
            pulse(RIGHT_PULSE, int(right_counter))
            right_steps -= int(right_counter)

            right_counter = right_counter % 1

    # Pulse any remaining right_steps from rounding or the special
    # case of left_steps = 0
    pulse(RIGHT_PULSE, right_steps)

    return (act_left, act_right)


# Servo actions

gpio_connection = pigpio.pi()

def pen_up(extent=PEN_EXTENT):
    gpio_connection.hardware_PWM(PWM, 50, int(PEN_DOWN + (PEN_UP - PEN_DOWN)*extent))
    time.sleep(0.5)

def pen_down():
    gpio_connection.hardware_PWM(PWM, 50, PEN_DOWN)
    time.sleep(0.5)


# Homing

def center():
    pen_up()

    # Outfeed the left until limit is tripped
    GPIO.output(LEFT_DIRECTION, GPIO.LOW)
    while GPIO.input(LEFT_LIMIT):
        pulse(LEFT_PULSE)

    # Infeed the left halfway to origin
    GPIO.output(LEFT_DIRECTION, GPIO.HIGH)
    pulse(LEFT_PULSE, 400)

    # Outfeed the right until limit is tripped
    GPIO.output(RIGHT_DIRECTION, GPIO.HIGH)
    while GPIO.input(RIGHT_LIMIT):
        pulse(RIGHT_PULSE)

    # Infeed the right to origin
    GPIO.output(RIGHT_DIRECTION, GPIO.LOW)
    pulse(RIGHT_PULSE, 800)

    # Finish up infeeding the left side
    pulse(LEFT_PULSE, 400)
    
    left = MAX_LEFT - 800 * STEP
    right = MAX_RIGHT - 800 * STEP

    origin_x = (left**2 - right**2 + L**2) / (2 * L)
    origin_y = sqrt(left**2 - origin_x**2)

    return left, right, origin_x, origin_y


# Queue consumption routine

def run_printer(q, completion):
    completion.value = -1   # -1 indicates no active job, otherwise a percentage

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(RIGHT_PULSE, GPIO.OUT)
    GPIO.setup(RIGHT_DIRECTION, GPIO.OUT)
    GPIO.setup(LEFT_PULSE, GPIO.OUT)
    GPIO.setup(LEFT_DIRECTION, GPIO.OUT)

    GPIO.output(RIGHT_PULSE, GPIO.HIGH)
    GPIO.output(RIGHT_DIRECTION, GPIO.HIGH)
    GPIO.output(LEFT_PULSE, GPIO.HIGH)
    GPIO.output(LEFT_DIRECTION, GPIO.LOW)

    GPIO.setup(LEFT_LIMIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_LIMIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pen_up()
    drawing = False

    left = right = origin_x = origin_y = -1

    while True:
        job = q.get()
        if job == 'STOP':
            break
        lines_max = lines_left = len(job)
        for l in [line.strip() for line in job]:
            lines_left -= 1
            completion.value = 1 - lines_left / lines_max

            if not l or l.startswith(';'):   # Blank line or comment
                continue
            elif l == 'G28':   # Centering routine (required before we can move in the coordinate system)
                left, right, origin_x, origin_y = center()
                drawing = False
            elif l.startswith('G0 '):   # Fast move (pen up)
                if drawing:
                    pen_up()
                    drawing = False
                m = re.search(r'G0 X(?P<x>-?\d+(\.\d*)?) Y(?P<y>-?\d+(\.\d*)?)', l)   # Normal X, Y coordinate move
                if m:
                    if origin_x < 0:
                        continue   # Refuse to move in the coordinate system if we have not centered
                    left, right = move_to(origin_x + float(m.group('x')), origin_y + -1 * float(m.group('y')), left, right)
                    continue
                m = re.search(r'G0 L(?P<left>-?\d+) R(?P<right>-?\d+)', l)   # Manual L, R step move
                if m:
                    left_shift, right_shift = int(m.group('left')), int(m.group('right'))
                    if left_shift > 0:
                        GPIO.output(LEFT_DIRECTION, GPIO.LOW)
                    else:
                        GPIO.output(LEFT_DIRECTION, GPIO.HIGH)
                    pulse(LEFT_PULSE, abs(left_shift))
                    if right_shift > 0:
                        GPIO.output(RIGHT_DIRECTION, GPIO.HIGH)
                    else:
                        GPIO.output(RIGHT_DIRECTION, GPIO.LOW)
                    pulse(RIGHT_PULSE, abs(right_shift))
                    left = right = origin_x = origin_y = -1   # Manual movements invalidate any calibrated coordinates
            elif l.startswith('G1 '):   # Draw (pen down)
                if origin_x < 0:
                    continue   # Refuse to move in the coordinate system if we have not centered
                if not drawing:
                    pen_down()
                    drawing = True
                m = re.search(r'G1 X(?P<x>-?\d+(\.\d*)?) Y(?P<y>-?\d+(\.\d*)?).*', l)
                if m:
                    left, right = move_to(origin_x + float(m.group('x')), origin_y + -1 * float(m.group('y')), left, right)

        completion.value = -1

    GPIO.cleanup()
