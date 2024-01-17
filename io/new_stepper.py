from gpiozero import OutputDevice, DigitalInputDevice
import time
from signal import pause

# Pin setup
dir_pin = 9
step_pin = 11
speed = 0.001
ms2_pin = 10

ms2 = OutputDevice(ms2_pin, initial_value = True)
direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)


def step_motor(steps, direction_flag):
    direction.value = direction_flag
    for _ in range(steps):
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)
try:
    while True:
        time.sleep(3)
        step_motor(100, 1)
        time.sleep(3)
        step_motor(100, 0)
    

except KeyboardInterrupt:
    print("Exiting program")
