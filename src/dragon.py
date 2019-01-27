import time

import settings

from dronekit import connect


def wakeup():
    """
    Wake up and connect to mavlink
    """
    print("Yawning...")
    print(settings.MAVLINK_ADDRESS)

    vehicle = connect(settings.MAVLINK_ADDRESS)

    while vehicle.location.global_relative_frame.alt < 10:
        v_alt = vehicle.location.global_relative_frame.alt
        print(">> Altitude = %.1f m" % v_alt)
        time.sleep(1)

