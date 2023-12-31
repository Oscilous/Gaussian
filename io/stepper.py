from gpiozero import OutputDevice, DigitalInputDevice
import time
from signal import pause

# Pin setup
ms1_pin = 3
ms2_pin = 17
ms3_pin = 27
solenoid_pin = 19
dir_pin = 4
step_pin = 2
end_switch_pin = 22
speed = 0.001
step_to_home = 20
# Initialize devices
solenoid = OutputDevice(solenoid_pin, initial_value=False)
direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)
end_switch = DigitalInputDevice(end_switch_pin, pull_up=True)

ms1 = OutputDevice(ms1_pin, initial_value=False)
ms2 = OutputDevice(ms2_pin, initial_value=True)
ms3 = OutputDevice(ms3_pin, initial_value=False)

def step_motor(steps, direction_flag):
    direction.value = direction_flag
    for _ in range(steps):
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)

def auto_home():
    direction.off()  # Towards end stop
    while end_switch.value:
        step.on()
        time.sleep(0.01)
        step.off()
        time.sleep(0.01)
    direction.on()  # Away from end stop
    step_motor(step_to_home, True)

def forward_90():
    step_motor(200, True)

def fast_auto_home():
    steps = 0
    direction.off()  # Towards end stop
    while end_switch.value:
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)
        steps = steps + 1
    direction.on()  # Away from end stop
    step_motor(step_to_home, True)

def shimmy():
    for i in range(0,5):
        step_motor(1, True)
        time.sleep(0.1)
    for i in range(0,5):
        step_motor(1, False)
        time.sleep(0.1)

try:
    auto_home()
    while True:
        time.sleep(1)
        forward_90()
        time.sleep(1)
        solenoid.on()
        forward_90()
        shimmy()
        solenoid.off()
        fast_auto_home()
        auto_home()
    

except KeyboardInterrupt:
    print("Exiting program")
