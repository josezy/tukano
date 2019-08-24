import time
import json
import redis
import logging
import settings

from datetime import datetime
##ARDUINO CONF
import serial, time
import json
BAUD_RATE = 9600
DEV_URL = '/dev/ttyACM0' 

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

    try:
		new_data = {
			'dt': str(datetime.now()),
            'pos': {
                'lat': position['lat'],
                'lon': position['lon'],
                'alt': position['alt'],
             }
  	    }
        arduino = serial.Serial(DEV_URL, BAUD_RATE)
		JSON=arduino.readline().decode("utf-8")
		JSON=json.loads(JSON[0:-2])
		new_data.update(JSON)
		arduino.close()
        logging.debug(new_data)
        redis_queue.lpush('TUKANO_DATA', json.dumps(new_data))
	except ValueError as e:
		logging.debug("BAD JSON")


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
