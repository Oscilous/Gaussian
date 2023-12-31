import cv2
import numpy as np
from picamera2 import Picamera2

IMG_DIMS = (1640, 1232)

picam2 = Picamera2(0)
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "YUV420"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

try:
    while True:
        im = picam2.capture_array()
        img_preproc = im[:IMG_DIMS[1], :IMG_DIMS[0]]
        img_preproc = cv2.resize(img_preproc, (IMG_DIMS[0], IMG_DIMS[1]))
        mask = np.zeros((IMG_DIMS[1], IMG_DIMS[0]), dtype="uint8")  # Adjusted mask shape
        # Draw a circle based on the trackbar values
        cv2.circle(mask, (1500, 1000), 1000, 255, -1)
        masked_image = cv2.bitwise_and(img_preproc, mask)

        # Apply thresholding to create a binary image
        _, binary = cv2.threshold(masked_image, 180, 255, cv2.THRESH_BINARY)
        cv2.imshow("Camera", binary)

        # Save an image when a key is pressed (e.g., 's')
        key = cv2.waitKey(1)

        # Exit the loop when 'q' is pressed
        if key == ord('q'):
            break

finally:
    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()
    picam2.close()
