import time
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
    flight_name = datetime.now().strftime("%Y_%m_%d_%H_%M")
    print("Running flight {}".format(flight_name))

    filename = "{}.json".format(flight_name)
    last_sample_ts = time.time()

    while True:
        try:
            drone_altitude = drone.location.global_relative_frame.alt
            enough_altitude = drone_altitude > settings.ALT_THRESHOLD
            elapsed_time = time.time() - last_sample_ts
            enough_timespan = elapsed_time > settings.DATA_COLLECT_TIMESPAN

            if enough_altitude and enough_timespan:
                last_sample_ts = time.time()
                collect_data(drone, filename)

        except Exception as e:
            # TODO: log errors
            raise e
