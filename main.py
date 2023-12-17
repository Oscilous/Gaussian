#python main.py 2> /dev/null
import cv2
import numpy as np
import matplotlib.pyplot as plt
from picamera2 import Picamera2
from libcamera import controls 
import time
import tkinter as tk
from tkinter import Button
from gpiozero import OutputDevice, DigitalInputDevice

# Pin setup
ms1_pin = 3
ms2_pin = 17
ms3_pin = 27
solenoid_pin = 19
dir_pin = 4
step_pin = 2
end_switch_pin = 22
speed = 0.0075

# Initialize devices
solenoid = OutputDevice(solenoid_pin, initial_value=False)
direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)
end_switch = DigitalInputDevice(end_switch_pin, pull_up=True)

#Init and set to half-step
ms1 = OutputDevice(ms1_pin, initial_value=True)
ms2 = OutputDevice(ms2_pin, initial_value=False)
ms3 = OutputDevice(ms3_pin, initial_value=False)

# Initial values for trackbars
IMG_DIMS = (1640, 1232)
initial_x, initial_y, initial_diameter = 808,612,380
initial_dev_up, initial_dev_down = 31,40
initial_threshold = 2000
initial_detection = 0

second_initial_x, second_initial_y, second_initial_diameter = 808,612,380
second_initial_dev_up, second_initial_dev_down = 31,40
second_initial_threshold = 2000

debug_mode = False
enable_plots = True
pause_mode = True
edit_mode = True
def step_motor(steps, direction_flag):
    direction.value = direction_flag
    for _ in range(steps):
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)

def auto_home():
    direction.off()  # Towards end stop
    while end_switch.value:
        step.on()
        time.sleep(0.02)
        step.off()
        time.sleep(0.02)
    direction.on()  # Away from end stop
    step_motor(9, True)

def fast_auto_home():
    steps = 0
    direction.off()  # Towards end stop
    while end_switch.value:
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)
        steps = steps + 1
    direction.on()  # Away from end stop
    step_motor(9, True)

def forward_90():
    step_motor(101, True)

def back_180():
    step_motor(200, False)

def nothing(val):
    pass

def update_mask():
    global Csys, Dia, pellet_center_mask, camera
    # Update circle parameters
    Csys = (cv2.getTrackbarPos("Circle_X", "Trackbars"),
            cv2.getTrackbarPos("Circle_Y", "Trackbars"))
    Dia = cv2.getTrackbarPos("Circle_Diameter", "Trackbars")

    # Create a black canvas the size of the camera feed
    pellet_center_mask = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
    # Draw a circle based on the trackbar values
    cv2.circle(pellet_center_mask, Csys, Dia, 255, -1)

def second_update_mask():
    global second_Csys, second_Dia, second_pellet_center_mask
    # Update circle parameters
    second_Csys = (cv2.getTrackbarPos("second_Circle_X", "Trackbars"),
            cv2.getTrackbarPos("second_Circle_Y", "Trackbars"))
    second_Dia = cv2.getTrackbarPos("second_Circle_Diameter", "Trackbars")

    # Create a black canvas the size of the camera feed
    second_pellet_center_mask = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
    # Draw a circle based on the trackbar values
    cv2.circle(second_pellet_center_mask, second_Csys, second_Dia, 255, -1)

def histogram_and_threshold(image, mask, camera):
    global masked_image, second_masked_image
    if camera == 1:
        # Apply the mask to the image
        masked_image = np.ma.array(image, mask=~mask)
        # Calculate the mean and standard deviation
        mean_value = np.mean(masked_image.compressed())
        std_dev_multiplier_upper = cv2.getTrackbarPos("Threshold_upper", "Trackbars")
        std_dev_multiplier_lower = cv2.getTrackbarPos("Threshold_lower", "Trackbars")
        work_image = masked_image
    elif camera == 2:
        second_masked_image = np.ma.array(image, mask=~mask)
        # Calculate the mean and standard deviation
        mean_value = np.mean(second_masked_image.compressed())
        std_dev_multiplier_upper = cv2.getTrackbarPos("second_Threshold_upper", "Trackbars")
        std_dev_multiplier_lower = cv2.getTrackbarPos("second_Threshold_lower", "Trackbars")
        work_image = second_masked_image

    # Calculate the threshold range
    lower_threshold = mean_value - std_dev_multiplier_lower
    upper_threshold = mean_value + std_dev_multiplier_upper
    
    if enable_plots:
        plot_histogram(work_image, lower_threshold, upper_threshold, std_dev_multiplier_lower, std_dev_multiplier_upper, mean_value)
    
    # Perform thresholding using mean and brightness deviation
    binary_image = ((work_image >= lower_threshold) & (work_image <= upper_threshold)).astype(np.uint8) * 255

    is_pellet_good = count_black_pixels(binary_image, mask, camera)
    return is_pellet_good
    
def create_trackbars():
    # Set up the window and trackbars
    cv2.namedWindow("Trackbars")

    # Create trackbars with default values
    cv2.createTrackbar("Circle_X", "Trackbars", initial_x, 5000, nothing)
    cv2.createTrackbar("Circle_Y", "Trackbars", initial_y, 5000, nothing)
    cv2.createTrackbar("Circle_Diameter", "Trackbars", initial_diameter, 2000, nothing)
    cv2.createTrackbar("Threshold_upper", "Trackbars", initial_dev_up, 60, nothing)
    cv2.createTrackbar("Threshold_lower", "Trackbars", initial_dev_down, 60, nothing)
    cv2.createTrackbar("Impurity_pixel_amount", "Trackbars", initial_threshold,10000, nothing)
    cv2.createTrackbar("detection_threshold", "Trackbars", initial_detection ,100, nothing)
    # Create trackbars with default values
    cv2.createTrackbar("second_Circle_X", "Trackbars", second_initial_x, 5000, nothing)
    cv2.createTrackbar("second_Circle_Y", "Trackbars", second_initial_y, 5000, nothing)
    cv2.createTrackbar("second_Circle_Diameter", "Trackbars", second_initial_diameter, 2000, nothing)
    cv2.createTrackbar("second_Threshold_upper", "Trackbars", second_initial_dev_up, 60, nothing)
    cv2.createTrackbar("second_Threshold_lower", "Trackbars", second_initial_dev_down, 60, nothing)
    cv2.createTrackbar("second_Impurity_pixel_amount", "Trackbars", second_initial_threshold,10000, nothing)


def count_black_pixels(binary_image, mask, camera):
    global masked_binary_image
    global second_masked_binary_image
    if camera == 1:
        # Apply the mask to the binary image
        masked_binary_image = cv2.bitwise_and(~binary_image, mask)
        # Count the black pixels (pixel values = 0) inside the masked area
        impurity_pixel_count = np.sum(masked_binary_image == 255)
    elif camera == 2:
        second_masked_binary_image = cv2.bitwise_and(~binary_image, mask)
        impurity_pixel_count = np.sum(second_masked_binary_image == 255)
    print(f'Impurities: {impurity_pixel_count}')
    impurity_threshold = cv2.getTrackbarPos("Impurity_pixel_amount", "Trackbars")
    if impurity_pixel_count > impurity_threshold:
        print("BAD")
        return False
    else:
        print("GOOD")
        return True

def plot_histogram(masked_image, lower_threshold, upper_threshold, std_dev_multiplier_lower, std_dev_multiplier_upper, mean_value):
    # Clear the previous plot
    plt.clf()
    flattened_data = masked_image.ravel()

    # Filter out the zeros
    data_without_zeros = flattened_data[flattened_data != 0]
    # Plot the histogram
    plt.hist(data_without_zeros, bins=256, density=True, alpha=0.6, color='g')

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
    plt.pause(0.1)

def is_pellet_present(image, mask):
    global masked_image
    masked_image = cv2.bitwise_and(image, mask)
    #Call update, as one of the displayed images have been updated
    update_window()
    # Apply thresholding to create a binary image
    _, binary = cv2.threshold(masked_image, 230, 255, cv2.THRESH_BINARY)
    impurity_pixel_count = np.sum(binary == 255)
    area_pixel_count = np.sum(mask == 255)
    detection_threshold = cv2.getTrackbarPos("detection_threshold", "Trackbars")
    percentage_light = int(impurity_pixel_count / area_pixel_count * 100)
    print(percentage_light)
    if percentage_light >  detection_threshold:
        return False
    else:
        return True
    
# Function to switch the current view based on button press
def update_window():
    global current_view, original_image, second_original_image, masked_image, masked_binary_image, second_masked_image, second_masked_binary_image
    if current_view == "original_image":
        try:
            cv2.destroyWindow("first_camera")
            cv2.destroyWindow("second_camera")
        except cv2.error as e:
            # Ignore the error if the window doesn't exist
            pass
        composite_image = np.hstack((original_image, second_original_image))
        height, width = composite_image.shape[:2]
        composite_image = cv2.resize(composite_image, (width // 2, height // 2))
        cv2.imshow("original_image", composite_image)
        cv2.waitKey(500)
    elif current_view == "first_camera":
        try:
            cv2.destroyWindow("original_image")
            cv2.destroyWindow("second_camera")
        except cv2.error as e:
            # Ignore the error if the window doesn't exist
            pass
        composite_image = np.hstack((masked_image, masked_binary_image))
        height, width = composite_image.shape[:2]
        composite_image = cv2.resize(composite_image, (width // 2, height // 2))
        cv2.imshow("first_camera", composite_image)
        cv2.waitKey(500)
    elif current_view == "second_camera":
        try:
            cv2.destroyWindow("original_image")
            cv2.destroyWindow("first_camera")
        except cv2.error as e:
            # Ignore the error if the window doesn't exist
            pass
        composite_image = np.hstack((second_masked_image, second_masked_binary_image))
        height, width = composite_image.shape[:2]
        composite_image = cv2.resize(composite_image, (width // 2, height // 2))
        cv2.imshow("second_camera", composite_image)
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
    masked_image_button = Button(root, text="First Camera", command=lambda: on_button_click("first_camera"))
    masked_image_button.pack(side="left")
    second_camera_button = Button(root, text="Second Camera", command=lambda: on_button_click("second_camera"))
    second_camera_button.pack(side="left")
    # Start Tkinter main loop
    root.update()
    root.update_idletasks()

#Setting up the pi cam
picam2 = Picamera2(1)
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "YUV420"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.set_controls({"ExposureTime": 1000})
picam2.start()

second_camera = Picamera2(0)
second_camera.preview_configuration.main.size = IMG_DIMS
second_camera.preview_configuration.main.format = "YUV420"
second_camera.preview_configuration.align()
second_camera.configure("preview")
second_camera.set_controls({"ExposureTime": 500})
second_camera.start()

# Create the Trackbars, so the mask can be created
current_view = "original_image"
# Create trackbars for adjusting mask
create_trackbars()
#Creating GUI
root = tk.Tk()
create_GUI()
#Creating blank canvas of images that will be rendered
original_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
second_original_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
masked_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
masked_binary_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")

second_masked_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
second_masked_binary_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")

auto_home()
# Main loop
while True:
    original_image = picam2.capture_array()
    original_image = original_image[:IMG_DIMS[1], :IMG_DIMS[0]]
    original_image = cv2.resize(original_image, (IMG_DIMS[0], IMG_DIMS[1]))
    #Make sure it is greyscale so we can use thresholding
    #original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    #As we've updated the original_image, it needs to be rerendered
    update_window()
    #Call update_mask, if adjustments were made with trackbars
    update_mask()
    #We check if the pellet is present

    if is_pellet_present(original_image, pellet_center_mask):
        time.sleep(0.1)
        print("Pellet")
        #Clear the previous image
        #Recapture, to ensure a fully stable image
        original_image = picam2.capture_array()
        original_image = original_image[:IMG_DIMS[1], :IMG_DIMS[0]]
        original_image = cv2.resize(original_image, (IMG_DIMS[0], IMG_DIMS[1]))
        #Preform relative mean based thresholding
        is_good_pellet = histogram_and_threshold(original_image, pellet_center_mask, 1)
        update_window()
        forward_90()
        time.sleep(0.25)
        if edit_mode:
            while True:
                update_window()
                #Call update_mask, if adjustments were made with trackbars
                second_update_mask()
                second_original_image = second_camera.capture_array()
                second_original_image = second_original_image[:IMG_DIMS[1], :IMG_DIMS[0]]
                second_original_image = cv2.resize(second_original_image, (IMG_DIMS[0], IMG_DIMS[1]))
                #Preform relative mean based thresholding
                is_good_pellet = histogram_and_threshold(second_original_image, second_pellet_center_mask, 2)
                root.update()
                root.update_idletasks()
        """
        second_original_image = second_camera.capture_array()
        second_original_image = second_original_image[:IMG_DIMS[1], :IMG_DIMS[0]]
        second_original_image = cv2.resize(second_original_image, (IMG_DIMS[0], IMG_DIMS[1]))
        """
        """
        if is_good_pellet:
            GPIO.output(solunoid, GPIO.LOW)
        else:
            GPIO.output(solunoid, GPIO.HIGH)
        """
        forward_90()
        time.sleep(1)
        """
        if is_good_pellet:
            GPIO.output(solunoid, GPIO.LOW)
        else:
            GPIO.output(solunoid, GPIO.LOW)
        """
        fast_auto_home()
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

# Release resources
cv2.destroyAllWindows()
