import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from picamera import PiCamera
from picamera.array import PiRGBArray
import time

camera = PiCamera()
camera.framerate = 10
camera.brightness = 47 #48 til clen mask5
camera.contrast = 1 #1 giver bedst detection
camera.shutter_speed = 10000
camera.exposure_mode = 'off'
camera.exposure_mode = 'backlight'
camera.awb_mode = 'fluorescent'
camera.resolution = (960, 960)
rawCapture = PiRGBArray(camera, size=camera.resolution)

pellet_center_mask = np.zeros(camera.resolution, dtype="uint8")
# Initial values for trackbars
initial_x, initial_y, initial_diameter = 480, 468, 350
threshold_value = 1.5
debug = 0
def nothing(val):
    pass

def update_mask():
    global Csys, Dia, pellet_center_mask
    # Update circle parameters
    Csys = (cv2.getTrackbarPos("Circle_X", "Trackbars"),
            cv2.getTrackbarPos("Circle_Y", "Trackbars"))
    Dia = cv2.getTrackbarPos("Circle_Diameter", "Trackbars")

    # Create a black canvas the size of the camera feed
    pellet_center_mask = np.zeros(camera.resolution, dtype="uint8")

    # Draw a circle based on the trackbar values
    cv2.circle(pellet_center_mask, Csys, Dia, 255, -1)
    if debug == 1:
        # Display the mask
        cv2.imshow("Pellet center mask", pellet_center_mask)

def histogram_and_threshold(image, mask):
    # Apply the mask to the image
    masked_image = np.ma.array(image, mask=~mask)
    # Convert the masked image to a regular NumPy array for visualization
    masked_image_display = masked_image.filled(fill_value=0).astype(np.uint8)
    # Calculate the mean and standard deviation
    mean_value = np.mean(masked_image.compressed())
    std_dev_value = np.std(masked_image.compressed())

    std_dev_multiplier_upper = cv2.getTrackbarPos("Threshold_upper", "Trackbars") / 10
    std_dev_multiplier_lower = cv2.getTrackbarPos("Threshold_lower", "Trackbars") / 10

    # Calculate the threshold range
    lower_threshold = mean_value - std_dev_multiplier_lower * std_dev_value
    upper_threshold = mean_value + std_dev_multiplier_upper * std_dev_value

    # Clear the previous plot
    plt.clf()

    # Plot the histogram
    plt.hist(masked_image.compressed(), bins=256, density=True, alpha=0.6, color='g')

    # Plot the fitted normal distribution
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mean_value, std_dev_value)
    plt.plot(x, p, 'k', linewidth=2)

    # Add vertical lines at thresholding points
    plt.axvline(x=lower_threshold, color='r', linestyle='--', label=f'Lower Threshold ({std_dev_multiplier_lower} std dev)')
    plt.axvline(x=upper_threshold, color='r', linestyle='--', label=f'Upper Threshold ({std_dev_multiplier_upper} std dev)')

    # Add labels and title
    plt.title(f'Mean = {mean_value:.2f}, Standard Deviation = {std_dev_value:.2f}')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')

    # Add legend
    plt.legend()

    # Pause for a short time to allow the plot window to update
    plt.pause(0.01)

    # Perform thresholding using mean and standard deviation
    binary_image = ((masked_image >= lower_threshold) & (masked_image <= upper_threshold)).astype(np.uint8) * 255

    # Display the original and thresholded images
    if debug == 1:
        cv2.imshow('Original Image', image)
        cv2.imshow('Masked image', masked_image_display)
    cv2.imshow('Thresholded Image', binary_image)
    count_black_pixels(binary_image, mask)
    

def create_trackbars():
    # Set up the window and trackbars
    cv2.namedWindow("Trackbars")

    # Create trackbars with default values
    cv2.createTrackbar("Circle_X", "Trackbars", initial_x, 960, nothing)
    cv2.createTrackbar("Circle_Y", "Trackbars", initial_y, 960, nothing)
    cv2.createTrackbar("Circle_Diameter", "Trackbars", initial_diameter, 500, nothing)
    cv2.createTrackbar("Threshold_upper", "Trackbars", 15, 20, nothing)
    cv2.createTrackbar("Threshold_lower", "Trackbars", 15, 20, nothing)
    cv2.createTrackbar("Impurity_pixel_amount", "Trackbars", 1000,50000, nothing)

def count_black_pixels(binary_image, mask):
    # Apply the mask to the binary image
    masked_binary_image = cv2.bitwise_and(~binary_image, mask)
    cv2.imshow("Counting black",masked_binary_image)
    # Count the black pixels (pixel values = 0) inside the masked area
    impurity_pixel_count = np.sum(masked_binary_image == 255)

    print(f'Impurities: {impurity_pixel_count}')
    impurity_threshold = cv2.getTrackbarPos("Impurity_pixel_amount", "Trackbars")
    if impurity_pixel_count > impurity_threshold:
        print("BAD")
    else:
        print("GOOD")


# Create the Trackbars, so the mask can be created
create_trackbars()
# Main loop
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):    #This would be the first thing in the big loop
    #original_image = cv2.imread('mask clean11.jpg' , cv2.IMREAD_GRAYSCALE)
    original_image = frame.array
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    update_mask()

    histogram_and_threshold(original_image, pellet_center_mask)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Press 'Esc' to exit
        break

# Release resources
cv2.destroyAllWindows()