import cv2
from picamera2 import Picamera2

IMG_DIMS = (3280, 2464)

picam2 = Picamera2()
picam2.preview_configuration.main.size = IMG_DIMS
picam2.preview_configuration.main.format = "YUV420"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

try:
    while True:
        im = picam2.capture_array()
        img_preproc = im[:IMG_DIMS[1], :IMG_DIMS[0]]
        cv2.imshow("Camera", img_preproc)

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