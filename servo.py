import time

import pigpio


pi = pigpio.pi()

print('Dead Center...')
pi.hardware_PWM(18, 50, 60000)

time.sleep(3)

print('Down...')
pi.hardware_PWM(18, 50, 110000)

time.sleep(1)

print('Done!')
