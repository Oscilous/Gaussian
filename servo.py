import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setwarnings(False)
servo_pin = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin,GPIO.OUT)
pwm = GPIO.PWM(servo_pin,50) 
pwm.start(0) #init af servo motor
time.sleep(1)
try:
    while True:
        pwm.ChangeDutyCycle(0)
        time.sleep(3)
        pwm.ChangeDutyCycle(6.8)
        time.sleep(3)
        pwm.ChangeDutyCycle(11.2)
        time.sleep(3)

except KeyboardInterrupt:
    print("Exiting gracefully")
    pwm.stop()
    GPIO.cleanup()