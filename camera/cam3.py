from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2

def setup_camera(camera):
    camera.framerate = 10
    camera.brightness = 47  # 48 til clen mask5
    camera.contrast = 1  # 1 giver bedst detection
    camera.shutter_speed = 10000
    camera.exposure_mode = 'off'
    camera.meter_mode = 'backlight'  # picamera uses 'meter_mode' instead of 'exposure_mode'
    camera.awb_mode = 'fluorescent'
    camera.resolution = (960, 960)

picam0 = PiCamera(camera_num=0)
picam1 = PiCamera(camera_num=1)
setup_camera(picam0)
setup_camera(picam1)

# Create PiRGBArray objects for capturing frames
rawCapture0 = PiRGBArray(picam0)
rawCapture1 = PiRGBArray(picam1)

try:
    for frame in picam0.capture_continuous(rawCapture0, format="bgr", use_video_port=True):
        original_image = frame.array
        cv2.imshow("camera 0", original_image)
        rawCapture0.truncate(0)  # Clear the stream to prepare for the next frame
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for frame in picam1.capture_continuous(rawCapture1, format="bgr", use_video_port=True):
        original_image_1 = frame.array
        cv2.imshow("camera 1", original_image_1)
        rawCapture1.truncate(0)  # Clear the stream to prepare for the next frame
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    picam0.close()
    picam1.close()
    cv2.destroyAllWindows()
