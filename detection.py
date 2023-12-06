import cv2
import numpy as np

# Initial values for trackbars
initial_x, initial_y, initial_diameter = 480, 468, 250
initial_dev_up, initial_dev_down = 23, 23
debug = 0
plots = 0
pellet_center_mask = np.zeros((960,960), dtype="uint8")

def nothing(val):
    pass

def update_mask():
    global Csys, Dia, pellet_center_mask, camera
    # Update circle parameters
    Csys = (cv2.getTrackbarPos("Circle_X", "Trackbars"),
            cv2.getTrackbarPos("Circle_Y", "Trackbars"))
    Dia = cv2.getTrackbarPos("Circle_Diameter", "Trackbars")

    # Create a black canvas the size of the camera feed
    pellet_center_mask = np.zeros((960, 960), dtype="uint8")
    # Draw a circle based on the trackbar values
    cv2.circle(pellet_center_mask, Csys, Dia, 255, -1)
    if debug == 1:
        # Display the mask
        cv2.imshow("Pellet center mask", pellet_center_mask)

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


def is_pellet_present(image, mask):
    masked_image = cv2.bitwise_and(image, mask)
    # Apply thresholding to create a binary image
    _, binary = cv2.threshold(masked_image, 225, 255, cv2.THRESH_BINARY)
    impurity_pixel_count = np.sum(binary == 255)
    area_pixel_count = np.sum(mask == 255)
    detection_threshold = cv2.getTrackbarPos("detection_threshold", "Trackbars")
    percentage_light = int(impurity_pixel_count / area_pixel_count * 100)
    cv2.putText(binary, "Percentage light:" + str(percentage_light) + "%",  (28,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(binary, "Percentage threshold:" + str(detection_threshold) + "%",  (28,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("Binary", binary)
    if percentage_light > detection_threshold:
        return False
    else:
        return True


# Create the Trackbars, so the mask can be created
create_trackbars()

while True:
    # Read a frame from the camera
    original_image = cv2.imread('no_pellet.jpg' , cv2.IMREAD_GRAYSCALE)
    update_mask()

    # Perform object detection qon the frame
    if is_pellet_present(original_image, pellet_center_mask):
        print("Pellet")
    else:
        print("No")
    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close all windows
cv2.destroyAllWindows()