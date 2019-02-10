# import redis
import settings

from datetime import datetime
from dronekit import connect

from tasks import collect_data

def wakeup():
    """
    Wake up and connect to mavlink
    """
    print("Yawning...")
    print(settings.MAVLINK_ADDRESS)

    dragone = connect(settings.MAVLINK_ADDRESS, wait_ready=True)

    return dragone

def fly_away(drone):
    """
    Call and perform neccesary tasks here
    """
    flight_name = datetime.now().strftime("%Y_%M_%d_%H_%M")
    print("Running flight {}".format(flight_name))

    filename = "{}.json".format(flight_name)
    # redis_queue = redis.Redis(**settings.REDIS_CONF)
    while True:
        try:
            drone_altitude = drone.location.global_relative_frame.alt
            if drone_altitude > settings.ALT_THRESHOLD:
                collect_data(drone, filename, settings.DATA_COLLECT_TIMESPAN)
        except Exception as e:
            # TODO: log errors
            raise e
