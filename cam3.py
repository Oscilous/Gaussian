from picamera2 import Picamera2, Preview
from libcamera import controls
from time import sleep

def configure_cam(camera):
    camera.resolution = (960, 960)
    camera.framerate = 10
    camera.brightness = 47  # 48 til clen mask5
    camera.contrast = 1  # 1 giver bedst detection
    camera.shutter_speed = 10000
    camera.exposure_mode = 'off'
    camera.meter_mode = 'backlight'  # picamera2 uses 'meter_mode' instead of 'exposure_mode'
    camera.awb_mode = 'fluorescent'
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})

picam0 = Picamera2(0)
picam1 = Picamera2(1)
configure_cam(picam0)
configure_cam(picam1)

try:
    picam0.start_preview(Preview.QTGL)
    picam1.start_preview(Preview.QTGL)
    picam0.start()
    picam1.start()

except KeyboardInterrupt:    
    picam0.stop()
    picam1.stop()
    picam0.stop_preview()
    picam1.stop_preview()