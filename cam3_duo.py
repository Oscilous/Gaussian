import time
from picamera2 import Picamera2, Preview

picam2a = Picamera2(0)
picam2a.configure(picam2a.create_preview_configuration())
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
picam2a.start_preview(Preview.QTGL)

picam2b = Picamera2(1)
picam2b.configure(picam2b.create_preview_configuration())
picam2b.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
picam2b.start_preview(Preview.QT)

picam2a.start()
picam2b.start()
time.sleep(100)
picam2a.stop_preview()
picam2b.stop_preview()