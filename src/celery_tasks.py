import json
import redis
import time
import Adafruit_DHT

import settings

from celery import Celery

app = Celery('tasks', broker=settings.CELERY_BROKER)
redis_queue = redis.Redis(**settings.REDIS_CONF)

@app.task
def am2302_measure():
    humidity, temperature = Adafruit_DHT.read_retry(
        Adafruit_DHT.AM2302,
        settings.AM2302_PINS['out']
    )
    data = {
        'ts': time.time(),
        'humidity': humidity,
        'temperature': temperature,
    }
    redis_queue.set('AM2302_data', json.dumps(data))
    return data

