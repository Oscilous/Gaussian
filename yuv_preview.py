import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls 
IMG_DIMS = (1640,1232)

picam2 = Picamera2(0)
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "YUV420"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

try:
    #controls = picam2.set_controls()
    #print(controls)
    while True:
        im = picam2.capture_array()
        img_preproc = im[:IMG_DIMS[1], :IMG_DIMS[0]]
        img_preproc = cv2.resize(img_preproc, (IMG_DIMS[0], IMG_DIMS[1]))
        # Save the image using OpenCV
        cv2.imshow("img_preproc", img_preproc)

finally:
    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()
    picam2.close()
