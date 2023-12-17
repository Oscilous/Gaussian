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
crash_pin = 26
speed = 0.005

# Initialize devices
solenoid = OutputDevice(solenoid_pin, initial_value=False)
direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)
end_switch = DigitalInputDevice(end_switch_pin, pull_up=True)
crash = OutputDevice(crash_pin, initial_value = False)

ms1 = OutputDevice(ms1_pin, initial_value=False)
ms2 = OutputDevice(ms2_pin, initial_value=False)
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
        time.sleep(0.02)
        step.off()
        time.sleep(0.02)
    direction.on()  # Away from end stop
    step_motor(9, True)

def forward_90():
    step_motor(101, True)

def fast_auto_home():
    steps = 0
    crash = False
    direction.off()  # Towards end stop
    while end_switch.value:
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)
        steps = steps + 1
        if steps > 230:
            crash = True
            pass
    if crash:
        pass
    direction.on()  # Away from end stop
    step_motor(9, True)

try:
    ms1.on()
    auto_home()
    while !crash:
        time.sleep(1)
        forward_90()
        time.sleep(1)
        solenoid.on()
        forward_90()
        time.sleep(1)
        solenoid.off()
        fast_auto_home()
        auto_home()
    

except KeyboardInterrupt:
    print("Exiting program")
