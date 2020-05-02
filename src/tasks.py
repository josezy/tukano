import json
import redis
import base64
import serial
import logging
import settings

from datetime import datetime
from util.util import append_json_file


logging.basicConfig(**settings.LOGGING_KWARGS)

redis_queue = redis.Redis(**settings.REDIS_CONF)
try:
    redis_queue.flushdb()
except redis.ConnectionError:
    logging.warn("Redis not available!!")


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
        # serial_device = serial.Serial(**settings.SERIAL_PARAMS)
        # json_data = json.loads(serial_device.readline().decode("utf-8"))
        # serial_device.close()
        import random
        json_data = {
            'MQ135': {
                'air_ppm': {
                    'units': 'ppm',
                    'value': random.randint(0, 1) + random.gauss(mu=0.5, sigma=0.1)
                },
                'air_temp': {
                    'units': 'celsius',
                    'value': random.randint(20, 22) + random.gauss(mu=0.5, sigma=0.1)
                }
            },
            'BMP183': {
                'altitude': {
                    'units': 'meters',
                    'value': random.randint(10, 11) + random.gauss(mu=0.5, sigma=0.1)
                },
                'temperature': {
                    'units': 'celsius',
                    'value': random.randint(20, 22) + random.gauss(mu=0.5, sigma=0.1)
                }
            }
        }
        sensors_data.update(json_data)

        try:
            redis_queue.lpush('TUKANO_DATA', json.dumps(sensors_data))
        except redis.ConnectionError:
            logging.warn("Redis not available!!")

        file_name = f"{datetime.now().strftime('%Y_%m_%d')}.json"
        append_json_file(file_name, sensors_data)

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
        try:
            sample = redis_queue.rpop('TUKANO_DATA')
        except redis.ConnectionError:
            logging.warn("Redis not available!!")
            break

        if not sample:
            break

        data.append(json.loads(sample))
        samples += 1

    return data and json.dumps(data)


def pack_frame(frame):
    if not settings.PROD:
        import cv2
        width = 640
        height = int(frame.shape[0] * width / frame.shape[1])
        frame = cv2.resize(
            frame, (width, height), interpolation=cv2.INTER_AREA)

        params = [cv2.IMWRITE_JPEG_QUALITY, settings.STREAM_VIDEO_JPEG_QUALITY]
        frame = cv2.imencode(".jpg", frame, params)[1]

    return base64.b64encode(frame)
