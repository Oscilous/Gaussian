import time
from picamera2 import Picamera2, Preview
from libcamera import controls

IMG_DIMS = (960, 960)

first_camera = Picamera2(0)
config = first_camera.create_preview_configuration()
config['main']['size'] = IMG_DIMS
config['main']['format'] = "YUV420"
first_camera.align_configuration(config)
print(config)
first_camera.configure(config)
first_camera.start()

#first_camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
#camera.shutter_speed = 10000
first_camera.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})
#first_camera.meter_mode = 'backlight'  # picamera uses 'meter_mode' instead of 'exposure_mode'
first_camera.set_controls({"AeConstraintMode": "Shadows"})
#first_camera.exposure_mode = 'off'
first_camera.set_controls({"AeEnable": "False"})
#first_camera.awb_mode = 'fluorescent'
first_camera.set_controls({"AwbMode": "Fluorescent"})

first_camera.start_preview(Preview.QTGL)


second_camera = Picamera2(1)
second_camera.configure(second_camera.create_preview_configuration())
second_camera.start_preview(Preview.QT)

second_camera.start()
time.sleep(100)
first_camera.stop_preview()
second_camera.stop_preview()