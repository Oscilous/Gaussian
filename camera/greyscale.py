import time
from picamera2 import Picamera2, Preview
from libcamera import controls
import cv2

IMG_DIMS = (1280, 720)

def setup_camera():
    picam = Picamera2()
    config = picam.create_preview_configuration()
    config['main']['size'] = IMG_DIMS
    config['main']['format'] = "YUV420"
    picam.align_configuration(config)
    print(config)
    picam.configure(config)
    picam.start()

    return picam

def main():
    picam = setup_camera()
    while True:
            # Hot loop (measured)
            img = picam.capture_array()
            img_preproc = img[:IMG_DIMS[1], :IMG_DIMS[0]]
            cv2.imshow("1", img_preproc)
            # End of hot loop