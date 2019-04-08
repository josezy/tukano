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

    _pic_dir = settings.PICS_DIR
    _vid_dir = settings.VIDEOS_DIR

    def __init__(self):
        from picamera import PiCamera
        self.cam = PiCamera()
        self.cam.rotation = 180

    def __del__(self):
        self.cam.close()
        self.cam = None

    def _ts_name(self):
        return time.strftime("%Y%m%d_%H%M%S")

    def take_pic(self, filename=None):
        pic_path = "{}/{}.jpg".format(
            self._pic_dir,
            filename or self._ts_name()
        )
        self.cam.capture(pic_path, use_video_port=True)

        return pic_path.split('/')[-1]

    def start_recording(self, filename=None):
        self.vid_path = "{}/{}.h264".format(
            self._vid_dir,
            filename or self._ts_name()
        )
        self.cam.start_recording(self.vid_path)
        
    def stop_recording(self):
        self.cam.stop_recording()
        return self.vid_path.split('/')[-1]

