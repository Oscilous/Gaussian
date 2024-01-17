from gpiozero import Button, OutputDevice, DigitalInputDevice
from signal import pause
import time
relay_pin = 26
relay = DigitalInputDevice(relay_pin, pull_up=True)

try:
    i =0
    while True:
        while relay.value:
            print(i)
            i = i + 1
            time.sleep(0.1)
            # Wait indefinitely for events
        pass
except KeyboardInterrupt:
    print("Exiting program")
