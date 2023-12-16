from gpiozero import OutputDevice, DigitalInputDevice
import time
from signal import pause

# Pin setup
solenoid_pin = 19
dir_pin = 4
step_pin = 2
end_switch_pin = 22
speed = 0.005

# Initialize devices
solenoid = OutputDevice(solenoid_pin, initial_value=False)
direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)
end_switch = DigitalInputDevice(end_switch_pin, pull_up=True)

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
    step_motor(7, True)

def forward_90():
    step_motor(50, True)

def back_180():
    step_motor(100, False)

try:
    auto_home()
    while True:
        time.sleep(1)
        forward_90()
        time.sleep(1)
        solenoid.on()
        forward_90()
        time.sleep(1)
        solenoid.off()
        back_180()
        auto_home()

except KeyboardInterrupt:
    print("Exiting program")