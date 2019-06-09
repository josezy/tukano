import time
import json
import redis
import logging
import settings

from datetime import datetime


logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=settings.LOGGING_LEVEL
)


redis_queue = redis.Redis(**settings.REDIS_CONF)
redis_queue.flushdb()


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

    # this is a syncronous job that blocks normal flow
    # TODO: run sensor mesasures async, then get the last sensed value here
    # am2302_data = am2302_measure()

    new_data = {
        'dt': str(datetime.now()),
        'pos': {
            'lat': position['lat'],
            'lon': position['lon'],
            'alt': position['alt'],
        },
        'am2302': "am2302_data",
        'bmp183': "bmp183_data"
    }

    logging.debug(new_data)
    redis_queue.lpush('TUKANO_DATA', json.dumps(new_data))


def prepare_data():
    samples = 0
    data = []
    while samples < settings.MAX_SAMPLES_PER_MAVLINK_MESSAGE:
        sample = redis_queue.rpop('TUKANO_DATA')
        if not sample:
            break

        data.append(json.loads(sample))
        samples += 1

    return data and json.dumps(data)


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
