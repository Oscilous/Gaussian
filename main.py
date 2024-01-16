#python main.py 2> /dev/null
import cv2
import numpy as np
import matplotlib.pyplot as plt
from picamera2 import Picamera2
from libcamera import controls 
import time
import tkinter as tk
from tkinter import Button, Radiobutton, StringVar
from gpiozero import OutputDevice, DigitalInputDevice
import json
from PIL import ImageTk, Image
from functools import partial

# Pin setup
ms1_pin = 3
ms2_pin = 17
ms3_pin = 27
solenoid_pin = 19
dir_pin = 4
step_pin = 2
end_switch_pin = 22
speed = 0.001
step_to_home = 20

# Initialize devices
solenoid = OutputDevice(solenoid_pin, initial_value=False)
direction = OutputDevice(dir_pin)
step = OutputDevice(step_pin)
end_switch = DigitalInputDevice(end_switch_pin, pull_up=True)

#Init and set to half-step
ms1 = OutputDevice(ms1_pin, initial_value=False)
ms2 = OutputDevice(ms2_pin, initial_value=True)
ms3 = OutputDevice(ms3_pin, initial_value=False)

# Initial values for trackbars
IMG_DIMS = (1640, 1232)
initial_x, initial_y, initial_diameter = 808,612,380
initial_dev_up, initial_dev_down = 31,40
initial_threshold = 2000
initial_detection = 0

second_initial_x, second_initial_y, second_initial_diameter = 884,691,511
second_initial_dev_up, second_initial_dev_down = 26,25
second_initial_threshold = 3000

debug_mode = False
enable_plots = False
pause_mode = True
edit_mode = False
calibration_cam_one = False
calibration_cam_two = False
first_camera_status = "Empty"
second_camera_status = "Waiting"
percentage__of_pellet = 0

font = cv2.FONT_HERSHEY_PLAIN

# Dictionary to store the initial values for each slider
initial_values = {
    "Circle_X": initial_x,
    "Circle_Y": initial_y,
    "Circle_Diameter": initial_diameter,
    "Threshold_upper": initial_dev_up,
    "Threshold_lower": initial_dev_down,
    "Impurity_pixel_amount": initial_threshold,
    "detection_threshold": initial_detection,
    "second_Circle_X": second_initial_x,
    "second_Circle_Y": second_initial_y,
    "second_Circle_Diameter": second_initial_diameter,
    "second_Threshold_upper": second_initial_dev_up,
    "second_Threshold_lower": second_initial_dev_down,
    "second_Impurity_pixel_amount": second_initial_threshold
}

def save_variables():
    data = {
        'initial_x': initial_values["Circle_X"], 'initial_y': initial_values["Circle_Y"], 'initial_diameter': initial_values["Circle_Diameter"],
        'initial_dev_up': initial_values["Threshold_upper"], 'initial_dev_down': initial_values["Threshold_lower"], 'initial_threshold': initial_values["Impurity_pixel_amount"],
        'initial_detection': initial_values["detection_threshold"], 'second_initial_x': initial_values["second_Circle_X"], 'second_initial_y': initial_values["second_Circle_Y"],
        'second_initial_diameter': initial_values["second_Circle_Diameter"], 'second_initial_dev_up': initial_values["second_Threshold_upper"], 'second_initial_dev_down': initial_values["second_Threshold_lower"],
        'second_initial_threshold': initial_values["second_Impurity_pixel_amount"]
    }
    with open('variables.json', 'w') as file:
        json.dump(data, file)

def load_variables():
    global initial_x, initial_y, initial_diameter
    global initial_dev_up, initial_dev_down, initial_threshold, initial_detection
    global second_initial_x, second_initial_y, second_initial_diameter
    global second_initial_dev_up, second_initial_dev_down, second_initial_threshold

    try:
        with open('variables.json', 'r') as file:
            data = json.load(file)

        # Assigning values from JSON to the global variables
        initial_values["Circle_X"] = data['initial_x']
        initial_values["Circle_Y"] = data['initial_y']
        initial_values["Circle_Diameter"] = data['initial_diameter']
        initial_values["Threshold_upper"] = data['initial_dev_up']
        initial_values["Threshold_lower"] = data['initial_dev_down']
        initial_values["Impurity_pixel_amount"] = data['initial_threshold']
        initial_values["detection_threshold"] = data['initial_detection']
        initial_values["second_Circle_X"] = data['second_initial_x']
        initial_values["second_Circle_Y"] = data['second_initial_y']
        initial_values["second_Circle_Diameter"] = data['second_initial_diameter']
        initial_values["second_Threshold_upper"] = data['second_initial_dev_up']
        initial_values["second_Threshold_lower"] = data['second_initial_dev_down']
        initial_values["second_Impurity_pixel_amount"] = data['second_initial_threshold']
    except FileNotFoundError:
        print("No saved variables found. Using default values.")

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
        time.sleep(0.01)
        step.off()
        time.sleep(0.01)
    direction.on()  # Away from end stop
    step_motor(step_to_home, True)

def fast_auto_home():
    direction.off()  # Towards end stop
    while end_switch.value:
        step.on()
        time.sleep(speed)
        step.off()
        time.sleep(speed)
    direction.on()  # Away from end stop
    step_motor(10, True)

def forward_90():
    step_motor(200, True)

def shimmy():
    for i in range(0,5):
        step_motor(1, True)
        time.sleep(0.05)
    for i in range(0,5):
        step_motor(1, False)
        time.sleep(0.05)

def nothing(val):
    pass

def update_mask():
    global Csys, Dia, pellet_center_mask, camera
    # Update circle parameters
    Csys = (initial_x, initial_y)
    Dia =  initial_diameter

    # Create a black canvas the size of the camera feed
    pellet_center_mask = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
    # Draw a circle based on the trackbar values
    cv2.circle(pellet_center_mask, Csys, Dia, 255, -1)

def second_update_mask():
    global second_Csys, second_Dia, second_pellet_center_mask
    # Update circle parameters
    second_Csys = (initial_x, initial_y)
    second_Dia = initial_diameter

    # Create a black canvas the size of the camera feed
    second_pellet_center_mask = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
    # Draw a circle based on the trackbar values
    cv2.circle(second_pellet_center_mask, second_Csys, second_Dia, 255, -1)

def histogram_and_threshold(image, mask, camera):
    global masked_image, second_masked_image, display_cam_one_masked_image, display_cam_two_masked_image
    if camera == 1:
        # Apply the mask to the image
        display_cam_one_masked_image = cv2.bitwise_and(image, mask);
        masked_image = np.ma.array(image, mask=~mask)
        update_window()
        # Calculate the mean and standard deviation
        mean_value = np.mean(masked_image.compressed())
        std_dev_multiplier_upper = initial_dev_up
        std_dev_multiplier_lower = initial_dev_down
        work_image = masked_image
    elif camera == 2:
        display_cam_two_masked_image = cv2.bitwise_and(image, mask);
        second_masked_image = np.ma.array(image, mask=~mask)
        display_cam_one_masked_image = masked_image
        second_update_mask()
        # Calculate the mean and standard deviation
        mean_value = np.mean(second_masked_image.compressed())
        std_dev_multiplier_upper = second_initial_dev_up
        std_dev_multiplier_lower = second_initial_dev_down
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
    impurity_threshold = impurity_threshold
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
    global masked_image, percentage__of_pellet
    masked_image = cv2.bitwise_and(image, mask)
    #Call update, as one of the displayed images have been updated
    update_window()
    # Apply thresholding to create a binary image
    #_, binary = cv2.threshold(masked_image, 100, 220, cv2.THRESH_BINARY)
    binary = cv2.inRange(masked_image, 100, 220)
    impurity_pixel_count = np.sum(binary == 255)
    area_pixel_count = np.sum(mask == 255)
    detection_threshold = initial_detection
    percentage__of_pellet = int(impurity_pixel_count / area_pixel_count * 100)
    if percentage__of_pellet >=  detection_threshold:
        return True
    else:
        return False
    
# Function to switch the current view based on button press
def update_window():
    global current_view, original_image, second_original_image, masked_image, masked_binary_image, second_masked_image, second_masked_binary_image, label
    if current_view == "original_image":
        top_composite_image = np.hstack((display_cam_one_masked_image, masked_binary_image))
        text_size_second = cv2.getTextSize(str(first_camera_status), font, 5, 2)[0]
        text_x_second = top_composite_image.shape[1] - text_size_second[0] - 15  # Left align, 10 pixels margin from the left
        text_y_second = top_composite_image.shape[0] - 10  # 10 pixels margin from the bottom
        cv2.putText(top_composite_image, str(first_camera_status), (text_x_second, text_y_second), font, 5, (255, 255, 255), 2, cv2.LINE_AA)
        
        status = str(str(percentage__of_pellet) + "%" + "of a pellet")
        text_x_status = 15
        text_y_status = top_composite_image.shape[0] - 10  # 10 pixels margin from the bottom
        cv2.putText(top_composite_image, status, (text_x_status, text_y_status), font, 5, (255, 255, 255), 2, cv2.LINE_AA)

        # Bot composite image is just a white image
        bot_composite_image = np.hstack((display_cam_two_masked_image, second_masked_binary_image))
        text_size_second = cv2.getTextSize(str(second_camera_status), font, 5, 2)[0]
        text_x_second = top_composite_image.shape[1] - text_size_second[0] - 15  # Left align, 10 pixels margin from the left
        text_y_second = top_composite_image.shape[0] - 10  # 10 pixels margin from the bottom
        cv2.putText(bot_composite_image, str(second_camera_status), (text_x_second, text_y_second), font, 5, (255, 255, 255), 2, cv2.LINE_AA)
        
        composite_image = np.vstack((top_composite_image, bot_composite_image))

    elif current_view == "first_camera_calibrate":
        top_composite_image = np.hstack((display_cam_one_masked_image, masked_binary_image))
        text_size_second = cv2.getTextSize(str(first_camera_status), font, 5, 2)[0]
        text_x_second = top_composite_image.shape[1] - text_size_second[0] - 15  # Left align, 10 pixels margin from the left
        text_y_second = top_composite_image.shape[0] - 10  # 10 pixels margin from the bottom
        cv2.putText(top_composite_image, str(first_camera_status), (text_x_second, text_y_second), font, 5, (255, 255, 255), 2, cv2.LINE_AA)

        white = np.full_like(second_masked_image, 255)
        bot_composite_image = np.hstack((white, white))

        composite_image = np.vstack((top_composite_image, bot_composite_image))

        

    elif current_view == "second_camera_calibrate":
        white = np.full_like(second_masked_image, 255)
        top_composite_image = np.hstack((white, white))

        bot_composite_image = np.hstack((display_cam_two_masked_image, second_masked_binary_image))
        text_size_second = cv2.getTextSize(str(second_camera_status), font, 5, 2)[0]
        text_x_second = top_composite_image.shape[1] - text_size_second[0] - 15  # Left align, 10 pixels margin from the left
        text_y_second = top_composite_image.shape[0] - 10  # 10 pixels margin from the bottom
        cv2.putText(bot_composite_image, str(second_camera_status), (text_x_second, text_y_second), font, 5, (255, 255, 255), 2, cv2.LINE_AA)

        composite_image = np.vstack((top_composite_image, bot_composite_image))

    new_width = int(composite_image.shape[1] * 0.4)
    new_height = int(composite_image.shape[0] * 0.4)
    new_size = (new_width, new_height)

    # Resize the image
    resized_composite_image = cv2.resize(composite_image, new_size)
    img = Image.fromarray(resized_composite_image)
    img_tk = ImageTk.PhotoImage(img)
    label.config(image=img_tk)
    label.image = img_tk
    time.sleep(0.1)

# Function to handle button clicks
def on_button_start():
    global current_view, calibration_cam_one, calibration_cam_two
    current_view = "original_image"
    calibration_cam_one = False
    calibration_cam_two = False

def on_save_button_clicked():
    save_variables()
    print("Variables saved.")

def on_calibrate_cam_one_button_clicked():
    global calibration_cam_one, current_view, calibration_cam_two
    calibration_cam_one = True
    calibration_cam_two = False
    current_view = "first_camera_calibrate"
    print("Calibration cam one mode: " + str(calibration_cam_one))

def on_calibrate_cam_two_button_clicked():
    global calibration_cam_two, current_view, calibration_cam_one
    calibration_cam_one = False
    calibration_cam_two = True
    current_view = "second_camera_calibrate"
    print("Calibration cam two mode: " + str(calibration_cam_two))


def on_slider_change(value):
    pass

def create_slider(window, name, row, col, from_, to):
    label = tk.Label(window, text=name)
    label.grid(row=row, column=col)
    slider = tk.Scale(window, from_=from_, to=to, orient=tk.HORIZONTAL,
                      command=partial(on_slider_change, name))
    slider.set(initial_values[name])  # Set to initial value
    slider.grid(row=row, column=col+1)
    return slider

# Function to be called when a slider value changes
def on_slider_change(slider_name, value):
    # Update the corresponding value in the dictionary
    initial_values[slider_name] = int(value)

def create_sliders_buttons():
    # Create button
    start_button = tk.Button(window, text="Start", command=on_button_start)
    start_button.grid(row=0, column=0)
    calibrate_cam_one_button = tk.Button(window, text="Calibrate Cam One", command=on_calibrate_cam_one_button_clicked)
    calibrate_cam_one_button.grid(row=1, column=0)
    calibrate_cam_two_button = tk.Button(window, text="Calibrate Cam Two", command=on_calibrate_cam_two_button_clicked)
    calibrate_cam_two_button.grid(row=2, column=0)
    save_variables_button = tk.Button(window, text="Save values", command=on_save_button_clicked)
    save_variables_button.grid(row=3, column=0)
    # Create slider

    create_slider(window, "Circle_X", 4, 0, 0, 5000)
    create_slider(window, "Circle_Y", 5, 0, 0, 5000)
    create_slider(window, "Circle_Diameter", 6, 0, 0, 2000)
    create_slider(window, "Threshold_upper", 7, 0, 0, 60)
    create_slider(window, "Threshold_lower", 8, 0, 0, 60)
    create_slider(window, "Impurity_pixel_amount", 9, 0, 0, 10000)
    create_slider(window, "detection_threshold", 10, 0, 0, 100)
    create_slider(window, "second_Circle_X", 11, 0, 0, 5000)
    create_slider(window, "second_Circle_Y", 12, 0, 0, 5000)
    create_slider(window, "second_Circle_Diameter", 13, 0, 0, 2000)
    create_slider(window, "second_Threshold_upper", 14, 0, 0, 60)
    create_slider(window, "second_Threshold_lower", 15, 0, 0, 60)
    create_slider(window, "second_Impurity_pixel_amount", 16, 0, 0, 10000)

load_variables()

#Setting up the pi cam
picam2 = Picamera2(0)
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "YUV420"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.set_controls({"ExposureTime": 500})
picam2.start()

second_camera = Picamera2(1)
second_camera.preview_configuration.main.size = IMG_DIMS
second_camera.preview_configuration.main.format = "YUV420"
second_camera.preview_configuration.align()
second_camera.configure("preview")
second_camera.set_controls({"ExposureTime": 500})
second_camera.start()

#Creating blank canvas of images that will be rendered
original_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
second_original_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
masked_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
masked_binary_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")

second_masked_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
second_masked_binary_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")

display_cam_one_masked_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")
display_cam_two_masked_image = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")

# Create the Trackbars, so the mask can be created
current_view = "original_image"
# Create trackbars for adjusting mask
#Creating GUI
window = tk.Tk()
window.attributes('-fullscreen', True)
window.title("Image Processing")

create_sliders_buttons()

# Create label for displaying the image
label = tk.Label(window)
label.grid(row=0, column=2, rowspan=window.grid_size()[1])
window.update()
window.update_idletasks()
update_window()

#auto_home()
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
        #Clear the previous image
        #Recapture, to ensure a fully stable image
        while(True): 
            original_image = picam2.capture_array()
            original_image = original_image[:IMG_DIMS[1], :IMG_DIMS[0]]
            original_image = cv2.resize(original_image, (IMG_DIMS[0], IMG_DIMS[1]))
            update_mask()
            update_window()
            #Preform relative mean based thresholding
            is_good_pellet = histogram_and_threshold(original_image, pellet_center_mask, 1)
            if is_good_pellet:
                first_camera_status = "Good"
            else:
                first_camera_status = "Bad"
                second_camera_status = "Pass"
            update_mask()
            update_window()
            # Update the Tkinter window
            window.update()
            window.update_idletasks()
            if calibration_cam_one: 
                continue
            else: 
                break

        if is_good_pellet:
            solenoid.off()
            forward_90()
            time.sleep(0.25)
            update_window()
            #Call update_mask, if adjustments were made with trackbars
            while True:
                second_update_mask()
                second_original_image = second_camera.capture_array()
                second_original_image = second_original_image[:IMG_DIMS[1], :IMG_DIMS[0]]
                second_original_image = cv2.resize(second_original_image, (IMG_DIMS[0], IMG_DIMS[1]))
                update_window()
                #Call update_mask, if adjustments were made with trackbars
                second_update_mask()
                #Preform relative mean based thresholding
                is_good_pellet = histogram_and_threshold(second_original_image, second_pellet_center_mask, 2)
                update_window()
                #Call update_mask, if adjustments were made with trackbars
                second_update_mask()
                if is_good_pellet:
                    solenoid.off()
                    second_camera_status = "Good"
                else:
                    solenoid.on()
                    second_camera_status = "Bad"
                update_window() 
                window.update()
                window.update_idletasks()
                if calibration_cam_two: 
                    continue
                else: 
                    break
        else:
            solenoid.on()
            forward_90()
        forward_90()
        shimmy()
        solenoid.off()
        first_camera_status = "Empty"
        second_camera_status = "Empty"
        fast_auto_home()
        auto_home()
    else:
        first_camera_status = "Empty"
        second_camera_status = "Empty"
    
    # Update the Tkinter window
    window.update()
    window.update_idletasks()
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Press 'Esc' to exit
        break
    # Clear the stream in preparation for the next frame

# Release resources
cv2.destroyAllWindows()
