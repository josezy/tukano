import time
import json
import redis
import settings

from datetime import datetime
from pymavlink import mavutil

from tasks import collect_data
from util.leds import error

redis_queue = redis.Redis(**settings.REDIS_CONF)


def wakeup():
    """
    Wake up and connect to mavlink
    """
    print("Yawning...")
    print(settings.MAVLINK_TUKANO['device'])

    while True:
        try:
            dragone = mavutil.mavlink_connection(**settings.MAVLINK_TUKANO)
            break
        except Exception as e:
            print(e)
            print("Retrying MAVLink vehicle connection...")

    dragone.wait_heartbeat()
    print("Hearbeat received!")

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
            position = drone.recv_match(
                type="GLOBAL_POSITION_INT",
                blocking=True
            )

            enough_altitude = position.alt > settings.ALT_THRESHOLD
            elapsed_time = time.time() - last_sample_ts
            enough_timespan = elapsed_time > settings.DATA_COLLECT_TIMESPAN

            if enough_altitude and enough_timespan:
                last_sample_ts = time.time()
                new_data = collect_data(position)
                if settings.VERBOSE:
                    print(new_data)
                redis_queue.lpush('TUKANO_DATA', json.dumps(new_data))

        except Exception as e:
            # TODO: log errors
            error()
            print(e)


if __name__ == "__main__":
    try:
        dragone = wakeup()
        fly_away(dragone)
    except:
        raise
