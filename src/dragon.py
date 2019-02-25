import time
import json
import redis
import settings

from datetime import datetime
from dronekit import connect

from tasks import collect_data

redis_queue = redis.Redis(**settings.REDIS_CONF)

def wakeup():
    """
    Wake up and connect to mavlink
    """
    print("Yawning...")
    print(settings.MAVLINK_VEHICLE_ADDRESS)

    dragone = None
    tries = 0

    while not dragone:
        try:
            dragone = connect(
                settings.MAVLINK_VEHICLE_ADDRESS,
                wait_ready=True
            )
        except Exception as e:
            tries += 1
            print("Try #{} failed: {}".format(tries, e))

    return dragone

def fly_away(drone):
    """
    Call and perform neccesary tasks here
    """
    flight_name = datetime.now().strftime("%Y_%m_%d_%H_%M")
    print("Running flight {}".format(flight_name))

    # Clean redis queue
    redis_queue.flushdb()

    last_sample_ts = time.time()

    while True:
        try:
            drone_altitude = drone.location.global_relative_frame.alt
            enough_altitude = drone_altitude > settings.ALT_THRESHOLD
            elapsed_time = time.time() - last_sample_ts
            enough_timespan = elapsed_time > settings.DATA_COLLECT_TIMESPAN

            if enough_altitude and enough_timespan:
                last_sample_ts = time.time()
                new_data = collect_data(drone)
                redis_queue.lpush('TUKANO_DATA', json.dumps(new_data))

        except Exception as e:
            # TODO: log errors
            raise e
