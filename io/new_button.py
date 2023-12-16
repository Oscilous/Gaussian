from gpiozero import Button, OutputDevice
from signal import pause

def button_pressed():
    print("HIGH")
    solenoid.on()

def button_released():
    print("LOW")
    solenoid.off()

button_pin = 22
solenoid_pin = 19

button = Button(button_pin, pull_up=True)
solenoid = OutputDevice(solenoid_pin)

button.when_pressed = button_pressed
button.when_released = button_released

try:
    pause()  # Wait indefinitely for events
except KeyboardInterrupt:
    print("Exiting program")
