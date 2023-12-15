from picamera import Picamera2, Preview
from libcamera import controls
from time import sleep

def setup_camera():
    global camera
    camera.framerate = 10
    camera.brightness = 47 #48 til clen mask5
    camera.contrast = 1 #1 giver bedst detection
    camera.shutter_speed = 10000
    camera.exposure_mode = 'off'
    camera.exposure_mode = 'backlight'
    camera.awb_mode = 'fluorescent'
    camera.resolution = (960, 960)
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})

picam0 = Picamera(0)
picam1 = Picamera(1)
setup_camera(picam0)
setup_camera(picam1)

try:
    picam0.start_preview(Preview.QTGL)
    picam1.start_preview(Preview.QTGL)
    picam0.start()
    picam1.start()
    with picam0.array.PiRGBArray(camera) as output:
        with picam1.array.PiRGBArray(camera) as output1:

        # You can capture the image and access the data in 'output' as needed
        camera.capture(output, format='rgb')
        image_data = output.array

except KeyboardInterrupt:    
    picam0.stop()
    picam1.stop()
    picam0.stop_preview()
    picam1.stop_preview()