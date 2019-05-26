import time
import settings
import logging

from pymavlink import mavutil

from tasks import collect_data
from camera import Camera
from util.leds import error, info, success


info()
logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=settings.LOGGING_LEVEL
)
logging.info("Initialising...")
logging.info(settings.MAVLINK_TUKANO['device'])


while True:
    try:
        drone = mavutil.mavlink_connection(**settings.MAVLINK_TUKANO)
        break
    except Exception as e:
        logging.warning(e)
        logging.warning("Retrying MAVLink vehicle connection...")


drone.wait_heartbeat()
logging.info("Hearbeat received!")

drone.mav.request_data_stream_send(
    drone.target_system,
    drone.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_POSITION,  # req_stream_id
    1,  # Rate in Hertz
    1  # Start/Stop
)


cam = Camera()

now = time.time()
timer_names = ['data_collect', 'take_pic']
last_tss = {tn: now for tn in timer_names}

vehicle = {
    'armed': False,
    'position': None
}

success()

while True:
    try:
        veh_msg = drone.recv_msg()
        veh_msg_type = veh_msg and veh_msg.get_type()
        if veh_msg_type != 'BAD_DATA':
            if veh_msg_type == 'HEARTBEAT':
                vehicle['armed'] = bool(veh_msg.base_mode // 128)
                logging.debug("VEHICLE: {}".format(vehicle))

            if veh_msg_type == 'GLOBAL_POSITION_INT':
                vehicle['position'] = {
                    'lat': veh_msg.lat,
                    'lon': veh_msg.lon,
                    'alt': veh_msg.alt,
                }
                logging.debug("VEHICLE: {}".format(vehicle))

        now = time.time()
        elapsed_times = {tn: now - last_tss[tn] for tn in timer_names}

        if elapsed_times['data_collect'] > settings.DATA_COLLECT_TIMESPAN:
            if vehicle['armed'] and vehicle['position']:
                if vehicle['position']['alt'] > settings.DATA_COLLECT_MIN_ALT:
                    collect_data(vehicle['position'])
                    last_tss['data_collect'] = now
                    logging.info("Data collected")

        if elapsed_times['take_pic'] > settings.TAKE_PIC_TIMESPAN:
            if vehicle['armed']:
                if vehicle['position']:
                    pic_name = cam.take_pic(gps_data={
                        'lat': float(vehicle['position']['lat']) / 10**7,
                        'lon': float(vehicle['position']['lon']) / 10**7,
                        'alt': float(vehicle['position']['alt']) / 10**3
                    })
                else:
                    pic_name = cam.take_pic()

                last_tss['take_pic'] = now
                logging.info("Pic taken '{}'".format(pic_name))

        if vehicle['armed'] and not cam.is_recording:
            vid_name = cam.start_recording()
            logging.info("Recording video '{}'".format(vid_name))

        if not vehicle['armed'] and cam.is_recording:
            cam.stop_recording()
            logging.info("Video recordered '{}'".format(vid_name))

    except Exception as e:
        # TODO: log errors
        error()
        logging.error(e)
