import time
import settings


def am2302_measure():
    import Adafruit_DHT
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


def collect_data(position):
    from datetime import datetime

    # this is a syncronous job that blocks normal flow
    # TODO: run sensor mesasures async, then get the last sensed value here
    am2302_data = am2302_measure()

    new_data = {
        'dt': str(datetime.now()),
        'pos': {
            'lat': float(position.lat) / 10**7,
            'lon': float(position.lon) / 10**7,
            'alt': float(position.alt) / 10**3,
        },
        'am2302': am2302_data,
    }
    return new_data





def take_pic():
    from picamera import PiCamera

    pic_name = "{}.jpg".format(time.strftime("%Y%m%d_%H%M%S"))
    pic_path = "{}/{}".format(settings.PICS_DIR, pic_name)

    with PiCamera() as cam:
        cam.rotation = 180
        cam.capture(pic_path)

    return pic_path


def extract_faces(pic_path):
    import os
    import face_recognition
    from PIL import Image

    image = face_recognition.load_image_file(pic_path)
    face_locations = face_recognition.face_locations(image)
    index = 0

    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)

        face_path = "{}/face_{}.jpg".format(settings.FACES_DIR, index)
        while os.path.isfile(face_path):
            index += 1
            face_path = "{}/face_{}.jpg".format(settings.FACES_DIR, index)

        pil_image.save(face_path)


class camera(object):
    """PiCamera class abstraction with custom methods"""

    cam = None

    def __init__(self):
        print("init...")
        from picamera import PiCamera
        self.cam = PiCamera()
        self.cam.rotation = 180

    def __del__(self):
        print("del...")
        del self.cam

    def start_recording(self, output_name):
        output_path = "{}/{}".format(settings.VIDEOS_DIR, output_name)
        self.cam.start_recording(output_path)
        
    def stop_recording(self):
        self.cam.stop_recording()

