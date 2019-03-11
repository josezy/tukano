import time
import Adafruit_DHT

import settings

def am2302_measure():
    humidity, temperature = Adafruit_DHT.read_retry(
        Adafruit_DHT.AM2302,
        settings.AM2302_PINS['out']
    )
    data = {
        'ts': time.time(),
        'humidity': float("{:.3f}".format(humidity)),
        'temperature': float("{:.3f}".format(temperature)),
    }
    return data

