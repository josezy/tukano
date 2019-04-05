import sys
import time
import Adafruit_DHT

from picamera import PiCamera

sys.path.append("..")
import settings

def am2302_measure():
    humidity, temperature = Adafruit_DHT.read_retry(
        Adafruit_DHT.AM2302,
        settings.AM2302_PINS['out']
    )
    # from random import random
    # humidity, temperature = 90 + 3 * random(), 17 + 3 * random()
    data = {
        'ts': time.time(),
        'humidity': float("{:.2f}".format(humidity)),
        'temperature': float("{:.2f}".format(temperature)),
    }
    return data

def take_pic():
    pic_name = time.strftime("%Y%m%d_%H%M%S")
    pic_path = "{}/{}.jpg".format(settings.PICS_DIR, pic_name)

    with PiCamera() as cam:
        cam.rotation = 180
        cam.capture(pic_path)
