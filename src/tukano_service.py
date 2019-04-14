import time
import json
import redis
import settings

from datetime import datetime
from pymavlink import mavutil

from tasks import collect_data, camera
from util.leds import error

redis_queue = redis.Redis(**settings.REDIS_CONF)

print("Initialising...")
print(settings.MAVLINK_TUKANO['device'])

while True:
    try:
        drone = mavutil.mavlink_connection(**settings.MAVLINK_TUKANO)
        break
    except Exception as e:
        print(e)
        print("Retrying MAVLink vehicle connection...")

drone.wait_heartbeat()
print("Hearbeat received!")

# Clean redis queue
redis_queue.flushdb()

flight_name = datetime.now().strftime("%Y_%m_%d_%H_%M")
print("Running flight {}".format(flight_name))

cam = camera()
cam.take_pic()

last_sample_ts = time.time()

while True:
    try:
        position = drone.recv_match(
            type="GLOBAL_POSITION_INT",
            blocking=True
        )
        
        elapsed_time = time.time() - last_sample_ts

        if elapsed_time > settings.DATA_COLLECT_TIMESPAN:
            collect_data(position)
            last_sample_ts = time.time()


    except Exception as e:
        # TODO: log errors
        error()
        print(e)
