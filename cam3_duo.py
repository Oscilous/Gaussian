import time
from picamera2 import Picamera2, Preview

first_camera = Picamera2(0)
first_camera.configure(first_camera.create_preview_configuration())
first_camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
first_camera.start_preview(Preview.QTGL)

second_camera = Picamera2(1)
second_camera.configure(second_camera.create_preview_configuration())
second_camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
second_camera.start_preview(Preview.QT)

first_camera.start()
second_camera.start()
time.sleep(100)
first_camera.stop_preview()
second_camera.stop_preview()