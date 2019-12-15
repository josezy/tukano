import json
import redis
import serial
import logging
import settings

from datetime import datetime


logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=settings.LOGGING_LEVEL
)


redis_queue = redis.Redis(**settings.REDIS_CONF)
redis_queue.flushdb()


def collect_data(position):
    sensors_data = {
        'dt': str(datetime.now()),
        'pos': {
            'lat': position['lat'],
            'lon': position['lon'],
            'alt': position['alt'],
        }
    }
    try:
        serial_device = serial.Serial(**settings.SERIAL_PARAMS)
        json_data = json.loads(serial_device.readline().decode("utf-8"))
        serial_device.close()

        sensors_data.update(json_data)
        redis_queue.lpush('TUKANO_DATA', json.dumps(sensors_data))
        logging.debug(sensors_data)
        logging.info("Data collected")
    except ValueError as e:
        logging.error("BAD JSON", e)
    except serial.SerialException as e:
        logging.error(f"Cannot connect to serial adquisition module: {e}")


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
