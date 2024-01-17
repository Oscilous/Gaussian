from gpiozero import OutputDevice, DigitalInputDevice
import time
from signal import pause

# Pin setup
ms2_pin = 2
dir_pin = 3
step_pin = 4
speed = 0.001

direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)

ms2 = OutputDevice(ms2_pin, initial_value=True)

def step_motor(steps, direction_flag):
    direction.value = direction_flag
    for _ in range(steps):
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)
try:
    while True:
        time.sleep(1)
        step_motor(10, 1)
        time.sleep(1)
        step_motor(10, 0)
    

except KeyboardInterrupt:
    print("Exiting program")
