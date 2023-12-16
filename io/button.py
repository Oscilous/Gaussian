import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button = 22
solunoid = 19
GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(solunoid, GPIO.OUT)
try:
    while True:
        button_state = GPIO.input(button)
        if button_state == GPIO.HIGH:
            print("HIGH")
            GPIO.output(solunoid, GPIO.HIGH)
        else:
            print("LOW")
            GPIO.output(solunoid, GPIO.LOW)
except KeyboardInterrupt:
    print("Exiting program")

finally:
    pass
    #GPIO.cleanup()
