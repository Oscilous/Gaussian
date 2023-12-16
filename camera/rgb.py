import cv2
import numpy as np
from picamera2 import Picamera2

IMG_DIMS = (3280, 2464)

picam2 = Picamera2()
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

try:
    controls = picam2.set_controls()
    print(controls)
    while True:
        im = picam2.capture_array()
        cv2.imshow("Camera", im)

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