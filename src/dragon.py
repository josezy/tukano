import settings

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
    collect_data(drone)
