import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import time
from PIL import Image
import io

resolution = (1640, 1232)

pellet_center_mask = np.zeros((resolution[1], resolution[0]), dtype="uint8")
# Initial values for trackbars
initial_x, initial_y, initial_diameter = 775, 700, 400
initial_dev_up, initial_dev_down = 23, 23
threshold_value = 1.5
debug = 1
buf = io.BytesIO()
def nothing(val):
    pass

def update_mask():
    global Csys, Dia, pellet_center_mask
    # Update circle parameters
    Csys = (cv2.getTrackbarPos("Circle_X", "Trackbars"),
            cv2.getTrackbarPos("Circle_Y", "Trackbars"))
    Dia = cv2.getTrackbarPos("Circle_Diameter", "Trackbars")

    # Create a black canvas the size of the camera feed
    pellet_center_mask = np.zeros((resolution[1], resolution[0]), dtype="uint8")

    # Draw a circle based on the trackbar values
    cv2.circle(pellet_center_mask, Csys, Dia, 255, -1)

def histogram_and_threshold(image, mask):
    global buf
    # Apply the mask to the image
    masked_image = np.ma.array(image, mask=~mask)
    # Convert the masked image to a regular NumPy array for visualization
    masked_image_display = masked_image.filled(fill_value=0).astype(np.uint8)
    # Calculate the mean and standard deviation
    mean_value = np.mean(masked_image.compressed())
    std_dev_value = np.std(masked_image.compressed())

    std_dev_multiplier_upper = cv2.getTrackbarPos("Threshold_upper", "Trackbars")
    std_dev_multiplier_lower = cv2.getTrackbarPos("Threshold_lower", "Trackbars")

    # Calculate the threshold range
    lower_threshold = mean_value - std_dev_multiplier_lower
    upper_threshold = mean_value + std_dev_multiplier_upper
    
        # Your existing code for creating the plot
    plt.clf()

    # Plot the histogram
    plt.hist(masked_image.compressed(), bins=256, range=(0, 255), density=True, alpha=0.6, color='g')

    # Plot the fitted normal distribution
    xmin, xmax = 0, 255
    plt.xlim(xmin, xmax)
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

    # Save the plot as "plot.jpg"
    #plt.savefig(f'{picture}_plot.jpg', bbox_inches='tight')

    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_image_pil = Image.open(buf)

    # Pause for a short time to allow the plot window to update
    plt.pause(0.01)
    
    # Perform thresholding using mean and standard deviation
    binary_image = ((masked_image >= lower_threshold) & (masked_image <= upper_threshold)).astype(np.uint8) * 255

    # Display the original and thresholded images
    if debug == 1:
        cv2.imshow('Masked image', masked_image_display)
    cv2.imshow('Thresholded Image', binary_image)
    #cv2.imwrite(f"{picture}_processed.jpg", binary_image)
    original_image = cv2.imread(f'{picture}.jpg')
    original_height, original_width = original_image.shape[:2]
    binary_height, binary_width = binary_image.shape[:2]
    
    # For a PIL Image, use the width and height attributes
    graph_width, graph_height = graph_image_pil.width, graph_image_pil.height

    # Calculate the total width and maximum height
    total_width = original_width + binary_width + graph_width
    max_height = max(original_height, binary_height, graph_height)
    # Convert NumPy arrays to PIL Images
    original_image_pil = Image.fromarray(original_image)
    binary_image_pil = Image.fromarray(binary_image)

    # Create a new blank image for the composite
    composite_image = Image.new('RGB', (total_width, max_height))

    # Paste the images into the composite image
    x_offset = 0
    for im in [original_image_pil, binary_image_pil, graph_image_pil]:
        composite_image.paste(im, (x_offset, 0))
        x_offset += im.width

    # Save the composite image
    composite_image.save(f'{picture}_output.jpg')
    count_black_pixels(binary_image, mask)
    

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

picture = "pellet"
# Create the Trackbars, so the mask can be created
create_trackbars()
# Main loop
try:
    # Load the image
    original_image = cv2.imread(f'{picture}.jpg', cv2.IMREAD_GRAYSCALE)

    # Check if the image is loaded properly
    if original_image is None:
        print("Error loading image. Check the file path and integrity.")
        
    #original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    update_mask()
    histogram_and_threshold(original_image, pellet_center_mask)
finally:
    # Release resources
    cv2.destroyAllWindows()