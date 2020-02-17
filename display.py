import functools
from time import sleep

import smbus

from lcd import LCD


display = LCD(0x27, 1)

display.lcd_puts('Hello', 1)
display.lcd_puts('Dolly', 2)
sleep(1)
display.lcd_puts('My Dear', 1)
sleep(1)
display.lcd_clear()
display.lcd_puts('Progress:', 1)
for i in range(0, 14):
    display.lcd_puts(str(i) + ('=' * i) + '>', 2)
    sleep(0.5)
sleep(2)
display.lcd_clear()

