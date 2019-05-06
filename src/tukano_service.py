import time
import settings

from pymavlink import mavutil

from tasks import collect_data
from camera import Camera
from util.leds import error


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


cam = Camera()

now = time.time()
timer_names = ['data_collect', 'take_pic']
last_tss = {tn: now for tn in timer_names}


while True:
    try:
        position = drone.recv_match(
            type="GLOBAL_POSITION_INT",
            blocking=True
        )

        now = time.time()
        elapsed_times = {tn: now - last_tss[tn] for tn in timer_names}

        if elapsed_times['data_collect'] > settings.DATA_COLLECT_TIMESPAN:
            collect_data(position)
            last_tss['data_collect'] = now

        if elapsed_times['take_pic'] > settings.TAKE_PIC_TIMESPAN and \
                position.alt > settings.DATA_COLLECT_MIN_ALT:
            cam.take_pic(gps_data={
                'lat': position.lat,
                'lon': position.lon,
                'alt': position.alt
            })
            last_tss['take_pic'] = now

        if position.alt > settings.RECORD_START_ALT and not cam.is_recording:
            cam.start_recording()

        if position.alt < settings.RECORD_STOP_ALT and cam.is_recording:
            cam.stop_recording()

    except Exception as e:
        # TODO: log errors
        error()
        print(e)
