import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls 
IMG_DIMS = (3280, 2464)

picam2 = Picamera2()
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")

picam2.set_controls({"AeConstraintMode": controls.AeConstraintModeEnum.ConstraintShadows})
#first_camera.exposure_mode = 'off'
picam2.set_controls({"AeEnable": 1})
#first_camera.awb_mode = 'fluorescent'
picam2.set_controls({"AwbMode": controls.AwbModeEnum.AwbFluorescent})

picam2.start()

try:
    metadata = picam2.capture_metadata()
    print(metadata)
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