import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button = 25
solunoid = 22
GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(solunoid, GPIO.OUT)
try:
    while True:
        button_state = GPIO.input(button)
        #if button_state == GPIO.HIGH:
        GPIO.output(solunoid, GPIO.HIGH)
        time.sleep(5)
        #else:
        GPIO.output(solunoid, GPIO.LOW)
        time.sleep(5)
except KeyboardInterrupt:
    print("Exiting program")

finally:
    pass
    #GPIO.cleanup()