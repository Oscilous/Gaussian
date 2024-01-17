from gpiozero import Button, OutputDevice
from signal import pause

def button_pressed():
    print("HIGH")

def button_released():
    print("LOW")

button_pin = 26

button = Button(button_pin, pull_up=True)

button.when_pressed = button_pressed
button.when_released = button_released

try:
    pause()  # Wait indefinitely for events
except KeyboardInterrupt:
    print("Exiting program")
