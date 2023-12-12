import RPi.GPIO as GPIO
import time

speed = 0.005
# Set GPIO pin numbers
solunoid = 22
DIR_PIN = 23  # Replace with your chosen GPIO pin number for direction
STEP_PIN = 24 # Replace with your chosen GPIO pin number for step
end_switch = 25
GPIO.cleanup()
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(solunoid, GPIO.OUT)
GPIO.output(solunoid, GPIO.LOW)
GPIO.setup(end_switch, GPIO.IN, GPIO.PUD_UP)

def home():
    GPIO.output(DIR_PIN, GPIO.LOW)  # To end stop
    while GPIO.input(end_switch) == GPIO.LOW:     
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.02)
    GPIO.output(DIR_PIN, GPIO.HIGH)  # Away from endstop
    for i in range (0, 8):     
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(speed)
        
def dispense_pellet():
    GPIO.output(DIR_PIN, GPIO.HIGH)  # Away from endstop
    for i in range (0, 50):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(speed)
def return_entrance():
    GPIO.output(DIR_PIN, GPIO.LOW)  # To  endstop
    for i in range (0, 100):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(speed)
        
try:
    home()
    i = 0
    while True:
        
        time.sleep(1)
        dispense_pellet()
        time.sleep(1)
        if i == 1:
            GPIO.output(solunoid, GPIO.HIGH)
        dispense_pellet()
        time.sleep(1)
        if i == 1:
            GPIO.output(solunoid, GPIO.LOW)
            i = 0
        return_entrance()
        i = i + 1
        
        
except KeyboardInterrupt:
    print("Exiting program")

finally:
    pass
    #DO NOT CLEAN UP, if cleaned stepper will float
    # Cleanup GPIO
    #GPIO.cleanup()