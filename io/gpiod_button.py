import gpiod
import time

# Define GPIO chip and pins
chip = gpiod.Chip('gpiochip4')
button_pin = 22
solenoid_pin = 19

# Setup GPIO
button_line = chip.get_line(button_pin)
solenoid_line = chip.get_line(solenoid_pin)
button_line.request(consumer='gpio_button', type=gpiod.LINE_REQ_EV_BOTH_EDGES)
solenoid_line.request(consumer='gpio_solenoid', type=gpiod.LINE_REQ_DIR_OUT)

try:
    while True:
        event = button_line.event_wait(sec=1)
        if event:
            button_event = button_line.event_read()
            if button_event.event_type == gpiod.LineEvent.RISING_EDGE:
                print("HIGH")
                solenoid_line.set_value(1)
            else:
                print("LOW")
                solenoid_line.set_value(0)
        time.sleep(0.1)  # To prevent high CPU usage

except KeyboardInterrupt:
    print("Exiting program")

finally:
    # Clean up
    button_line.release()
    solenoid_line.release()
