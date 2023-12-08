import RPi.GPIO as GPIO
import time

# Set GPIO pin numbers
DIR_PIN = 2  # Replace with your chosen GPIO pin number for direction
STEP_PIN = 3 # Replace with your chosen GPIO pin number for step

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(DIR_PIN, GPIO.HIGH)  # Set to GPIO.LOW for opposite direction

        # Step the motor
        for _ in range(100):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.001)
        GPIO.output(DIR_PIN, GPIO.LOW)  # Set to GPIO.LOW for opposite direction

        # Step the motor
        for _ in range(100):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.001)

except KeyboardInterrupt:
    print("Exiting program")

finally:
    # Cleanup GPIO
    GPIO.cleanup()