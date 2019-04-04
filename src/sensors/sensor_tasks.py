import sys
import time
import Adafruit_DHT

sys.path.append("..")
import settings

def am2302_measure():
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

