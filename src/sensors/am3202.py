import Adafruit_DHT

from datetime import timedelta

class AM2302():
    """AM2302 temperature and humidity sensor"""
    def __init__(self,
                 pin=4,
                 redis_queue=None,
                 interval=timedelta(seconds=1)):
        self.sensor_type = Adafruit_DHT.AM2302
        self.pin = pin
        self.redis_queue = redis_queue

        if redis_queue:
            """
            Start async periodic task with interval and save in redis
                redis.set(self.__class__.__name__, data)
            """
            pass 

    def data(self):
        if self.redis_queue:
            json_data = self.redis_queue.get(self.__class__.__name__)
            raw_data = json.loads(json_data)
            _data = (raw_data['humidity'], raw_data['temperature'])
        else:
            _data = Adafruit_DHT.read_retry(
                self.sensor_type,
                self.pin
            )
        return _data