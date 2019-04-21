import time
import json
import redis
import settings

from datetime import datetime


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
    if position.alt < settings.DATA_COLLECT_MIN_ALT:
        return

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

    if settings.VERBOSE:
        print(new_data)
    redis_queue.lpush('TUKANO_DATA', json.dumps(new_data))
