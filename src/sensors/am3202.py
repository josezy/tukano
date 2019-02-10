import time
import json
import Adafruit_DHT

from ..celery_tasks import compute_data

class AM2302():
    """AM2302 temperature and humidity sensor"""
    def __init__(self,
                 pin=4,
                 redis_queue=None,
                 interval=1.0):
        self.sensor_type = Adafruit_DHT.AM2302
        self.pin = pin
        self.redis_queue = redis_queue
        self.data = None

        if redis_queue:
            """
            Start async periodic task with interval and save in redis
                redis.set(self.__class__.__name__, data)
            """
            # TODO: add this to beat schedule (make periodic)
            compute_data.delay(self.measure)

    def measure(self, *args, **kwargs):
        humidity, temperature = Adafruit_DHT.read_retry(
            self.sensor_type,
            self.pin
        )
        self.data = {
            'ts': time.time(),
            'humidity': humidity,
            'temperature': temperature,
        }
        if self.redis_queue:
            self.redis_queue.set(
                self.__class__.__name__,
                json.dumps(self.data)
            )

    def data(self):
        if self.data:
            return self.data

        if self.redis_queue:
            return self.redis_queue.get(self.__class__.__name__)