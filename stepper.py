import RPi.GPIO as GPIO
import time

# Set GPIO pin numbers
DIR_PIN = 23  # Replace with your chosen GPIO pin number for direction
STEP_PIN = 24 # Replace with your chosen GPIO pin number for step
end_switch = 25
EN_PIN = 7
GPIO.cleanup()
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.setup(end_switch, GPIO.IN, GPIO.PUD_UP)
try:
    GPIO.output(EN_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, GPIO.LOW)  # Set to GPIO.LOW for opposite direction
    while GPIO.input(end_switch) == GPIO.LOW:     
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)
    # Cleanup GPIO
    GPIO.output(STEP_PIN, GPIO.LOW)
    GPIO.output(EN_PIN, GPIO.HIGH)
        
        
except KeyboardInterrupt:
    print("Exiting program")

finally:
    pass
    #DO NOT CLEAN UP, if cleaned stepper will float
    # Cleanup GPIO
    #GPIO.cleanup()