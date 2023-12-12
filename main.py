#python main.py 2> /dev/null
import cv2
import numpy as np
import matplotlib.pyplot as plt
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import tkinter as tk
from tkinter import Button
import RPi.GPIO as GPIO

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
# Initial values for trackbars
initial_x, initial_y, initial_diameter = 480, 468, 250
initial_dev_up, initial_dev_down = 23, 23
debug_mode = False
enable_plots = False
pause_mode = True

def nothing(val):
    pass

def setup_camera():
    global camera
    camera.framerate = 10
    camera.brightness = 47 #48 til clen mask5
    camera.contrast = 1 #1 giver bedst detection
    camera.shutter_speed = 10000
    camera.exposure_mode = 'off'
    camera.exposure_mode = 'backlight'
    camera.awb_mode = 'fluorescent'
    camera.resolution = (960, 960)

def update_mask():
    global Csys, Dia, pellet_center_mask, camera
    # Update circle parameters
    Csys = (cv2.getTrackbarPos("Circle_X", "Trackbars"),
            cv2.getTrackbarPos("Circle_Y", "Trackbars"))
    Dia = cv2.getTrackbarPos("Circle_Diameter", "Trackbars")

    # Create a black canvas the size of the camera feed
    pellet_center_mask = np.zeros(camera.resolution, dtype="uint8")
    # Draw a circle based on the trackbar values
    cv2.circle(pellet_center_mask, Csys, Dia, 255, -1)

def histogram_and_threshold(image, mask):
    # Apply the mask to the image
    masked_image = np.ma.array(image, mask=~mask)
    # Calculate the mean and standard deviation
    mean_value = np.mean(masked_image.compressed())

    std_dev_multiplier_upper = cv2.getTrackbarPos("Threshold_upper", "Trackbars")
    std_dev_multiplier_lower = cv2.getTrackbarPos("Threshold_lower", "Trackbars")

    # Calculate the threshold range
    lower_threshold = mean_value - std_dev_multiplier_lower
    upper_threshold = mean_value + std_dev_multiplier_upper
    
    if enable_plots:
        plot_histogram()
    
    # Perform thresholding using mean and brightness deviation
    binary_image = ((masked_image >= lower_threshold) & (masked_image <= upper_threshold)).astype(np.uint8) * 255

    is_pellet_good = count_black_pixels(binary_image, mask)
    return is_pellet_good
    
def create_trackbars():
    # Set up the window and trackbars
    cv2.namedWindow("Trackbars")

    # Create trackbars with default values
    cv2.createTrackbar("Circle_X", "Trackbars", initial_x, 960, nothing)
    cv2.createTrackbar("Circle_Y", "Trackbars", initial_y, 960, nothing)
    cv2.createTrackbar("Circle_Diameter", "Trackbars", initial_diameter, 500, nothing)
    cv2.createTrackbar("Threshold_upper", "Trackbars", initial_dev_up, 40, nothing)
    cv2.createTrackbar("Threshold_lower", "Trackbars", initial_dev_down, 40, nothing)
    cv2.createTrackbar("Impurity_pixel_amount", "Trackbars", 1000,50000, nothing)
    cv2.createTrackbar("detection_threshold", "Trackbars", 40,100, nothing)

def count_black_pixels(binary_image, mask):
    global masked_binary_image
    # Apply the mask to the binary image
    masked_binary_image = cv2.bitwise_and(~binary_image, mask)
    # Count the black pixels (pixel values = 0) inside the masked area
    impurity_pixel_count = np.sum(masked_binary_image == 255)

    print(f'Impurities: {impurity_pixel_count}')
    impurity_threshold = cv2.getTrackbarPos("Impurity_pixel_amount", "Trackbars")
    if impurity_pixel_count > impurity_threshold:
        return False
    else:
        return True


def plot_histogram():
    global masked_image
    global lower_threshold
    global upper_threshold
    global std_dev_multiplier_lower
    global std_dev_multiplier_upper
    global mean_value
    # Clear the previous plot
    plt.clf()

    # Plot the histogram
    plt.hist(masked_image.compressed(), bins=256, density=True, alpha=0.6, color='g')

    # Add vertical lines at thresholding points
    plt.axvline(x=lower_threshold, color='r', linestyle='--', label=f'Lower Threshold ({std_dev_multiplier_lower} std dev)')
    plt.axvline(x=upper_threshold, color='r', linestyle='--', label=f'Upper Threshold ({std_dev_multiplier_upper} std dev)')

    # Add labels and title
    plt.title(f'Mean = {mean_value:.2f}')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')

    # Add legend
    plt.legend()

    # Pause for a short time to allow the plot window to update
    plt.pause(0.01)

def is_pellet_present(image, mask):
    global masked_image
    masked_image = cv2.bitwise_and(image, mask)
    #Call update, as one of the displayed images have been updated
    update_window()
    # Apply thresholding to create a binary image
    _, binary = cv2.threshold(masked_image, 240, 255, cv2.THRESH_BINARY)
    impurity_pixel_count = np.sum(binary == 255)
    area_pixel_count = np.sum(mask == 255)
    detection_threshold = cv2.getTrackbarPos("detection_threshold", "Trackbars")
    percentage_light = int(impurity_pixel_count / area_pixel_count * 100)
    print(percentage_light)
    if percentage_light > detection_threshold:
        return False
    else:
        return True
    
# Function to switch the current view based on button press
def update_window():
    global current_view, original_image, masked_image, masked_binary_image
    if current_view == "original_image":
        try:
            cv2.destroyWindow("masked_image")
            cv2.destroyWindow("masked_binary_image")
        except cv2.error as e:
            # Ignore the error if the window doesn't exist
            pass
        cv2.imshow("original_image", original_image)
        cv2.waitKey(500)
    elif current_view == "masked_image":
        try:
            cv2.destroyWindow("original_image")
            cv2.destroyWindow("masked_binary_image")
        except cv2.error as e:
            # Ignore the error if the window doesn't exist
            pass
        cv2.imshow("masked_image", masked_image)
        cv2.waitKey(500)
    elif current_view == "masked_binary_image":
        try:
            cv2.destroyWindow("original_image")
            cv2.destroyWindow("masked_image")
        except cv2.error as e:
            # Ignore the error if the window doesn't exist
            pass
        cv2.imshow("masked_binary_image", masked_binary_image)
        cv2.waitKey(500)
# Function to handle button clicks
def on_button_click(view_name):
    global current_view
    current_view = view_name

def create_GUI():
    global root
    # Create Tkinter window
    root.title("OpenCV Viewer")
    original_image_button = Button(root, text="Original Image", command=lambda: on_button_click("original_image"))
    original_image_button.pack(side="left")
    masked_image_button = Button(root, text="Masked Image", command=lambda: on_button_click("masked_image"))
    masked_image_button.pack(side="left")
    masked_binary_image_button = Button(root, text="Masked Binary Image", command=lambda: on_button_click("masked_binary_image"))
    masked_binary_image_button.pack(side="left")
    # Start Tkinter main loop
    root.update()
    root.update_idletasks()

#Setting up the pi cam
camera = PiCamera()
setup_camera()
rawCapture = PiRGBArray(camera, size=camera.resolution)
# Create the Trackbars, so the mask can be created
current_view = "original_image"
# Create trackbars for adjusting mask
create_trackbars()
#Creating GUI
root = tk.Tk()
create_GUI()
#Creating blank canvas of images that will be rendered
original_image = np.zeros(camera.resolution, dtype="uint8")
masked_image = np.zeros(camera.resolution, dtype="uint8")
masked_binary_image = np.zeros(camera.resolution, dtype="uint8")
auto_home()
# Main loop
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):    #This would be the first thing in the big loop
    #original_image = cv2.imread('mask clean11.jpg' , cv2.IMREAD_GRAYSCALE)
    #Read the image from the raspberry pi
    original_image = frame.array
    #Make sure it is greyscale so we can use thresholding
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    #As we've updated the original_image, it needs to be rerendered
    update_window()
    #Call update_mask, if adjustments were made with trackbars
    update_mask()
    #We check if the pellet is present
    
    if is_pellet_present(original_image, pellet_center_mask):
        print("Pellet")
        #Clear the previous image
        rawCapture.truncate(0)
        #Recapture, to ensure a fully stable image
        original_image = frame.array
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        #Preform relative mean based thresholding
        is_good_pellet = histogram_and_threshold(original_image, pellet_center_mask)
        update_window()
        forward_90()
        time.sleep(1)
        if is_good_pellet:
            GPIO.output(solunoid, GPIO.HIGH)
        else:
            GPIO.output(solunoid, GPIO.LOW)
        forward_90()
        time.sleep(1)
        if is_good_pellet:
            GPIO.output(solunoid, GPIO.LOW)
        else:
            GPIO.output(solunoid, GPIO.LOW)
        back_180()
        auto_home()
    else:
        print("No")
    
    # Update the Tkinter window
    root.update()
    root.update_idletasks()
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Press 'Esc' to exit
        break
    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)

# Release resources
cv2.destroyAllWindows()
