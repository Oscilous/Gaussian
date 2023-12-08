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
        pwm.ChangeDutyCycle(2.5)
        #pwm.stop()
        time.sleep(2)
        #pwm.start(0)
        pwm.ChangeDutyCycle(7.5)
        #pwm.stop()
        time.sleep(2)
        #pwm.start(0)
        pwm.ChangeDutyCycle(12.5)
        #pwm.stop()
        time.sleep(2)
        #pwm.start(0)
        
        

except KeyboardInterrupt:
    print("Exiting gracefully")
    pwm.stop()
    GPIO.cleanup()