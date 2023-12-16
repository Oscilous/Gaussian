import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls 
IMG_DIMS = (3280, 2464)

picam2 = Picamera2()
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "YUV420"
picam2.preview_configuration.align()
picam2.configure("preview")

#picam2.set_controls({"AeConstraintMode": controls.AeConstraintModeEnum.Shadows})
#picam2.set_controls({"AeEnable": 1})
#picam2.set_controls({"AwbMode": controls.AwbModeEnum.Fluorescent})

picam2.start()

try:
    metadata = picam2.capture_metadata()
    print(metadata)
    im = picam2.capture_array()
    img_preproc = im[:IMG_DIMS[1], :IMG_DIMS[0]]
    img_preproc = cv2.resize(img_preproc, (IMG_DIMS[0], IMG_DIMS[1]))
    # Save the image using OpenCV
    cv2.imwrite("raw.jpg", img_preproc)

finally:
    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()
    picam2.close()