import time
import settings

from pymavlink import mavutil

from tasks import collect_data
from camera import Camera
from util.leds import error, info, success


info()
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

status = 'allgood'

while True:

    if status == 'allgood':
        success()

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
            if settings.VERBOSE_LEVEL <= 2:
                print("[INFO] Data collected")

        if elapsed_times['take_pic'] > settings.TAKE_PIC_TIMESPAN and \
                position.alt > settings.DATA_COLLECT_MIN_ALT:
            pic_name = cam.take_pic(gps_data={
                'lat': float(position.lat) / 10**7,
                'lon': float(position.lon) / 10**7,
                'alt': float(position.alt) / 10**3
            })
            last_tss['take_pic'] = now
            if settings.VERBOSE_LEVEL <= 2:
                print("[INFO] Pic taken '{}'".format(pic_name))

        if position.alt > settings.RECORD_START_ALT and not cam.is_recording:
            vid_name = cam.start_recording()
            if settings.VERBOSE_LEVEL <= 2:
                print("[INFO] Recording video '{}'".format(vid_name))

        if position.alt < settings.RECORD_STOP_ALT and cam.is_recording:
            cam.stop_recording()
            if settings.VERBOSE_LEVEL <= 2:
                print("[INFO] Video recordered at '{}'".format(vid_name))

    except Exception as e:
        # TODO: log errors
        status = 'error'
        error()
        print(e)
