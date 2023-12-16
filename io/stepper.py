import RPi.GPIO as GPIO
import time

GPIO.cleanup()
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

def auto_home():
    GPIO.output(DIR_PIN, GPIO.LOW)  # To end stop
    while GPIO.input(end_switch) == GPIO.LOW:     
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.02)
    GPIO.output(DIR_PIN, GPIO.HIGH)  # Away from endstop
    for i in range (0, 7):     
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(speed)
        
def forward_90():
    GPIO.output(DIR_PIN, GPIO.HIGH)  # Away from endstop
    for i in range (0, 50):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(speed)
def back_180():
    GPIO.output(DIR_PIN, GPIO.LOW)  # To  endstop
    for i in range (0, 100):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(speed)
        
try:
    auto_home()
    i = 0
    while True:
        time.sleep(1)
        forward_90()
        time.sleep(1)
        GPIO.output(solunoid, GPIO.HIGH)
        forward_90()
        time.sleep(1)
        GPIO.output(solunoid, GPIO.LOW)
        back_180()
        auto_home()
        
        
except KeyboardInterrupt:
    print("Exiting program")

finally:
    pass
    #DO NOT CLEAN UP, if cleaned stepper will float
    # Cleanup GPIO
    #GPIO.cleanup()