import ssl
import time
import settings
import logging

from pymavlink import mavutil
from websocket import create_connection

from tasks import collect_data, prepare_data
from camera import Camera
from util import leds


leds.info()
logging.basicConfig(
    format=settings.LOGGING_FORMAT,
    level=settings.LOGGING_LEVEL
)
logging.info(f"Initialising vehicle at {settings.MAVLINK_TUKANO['device']}")


while True:
    try:
        drone = mavutil.mavlink_connection(**settings.MAVLINK_TUKANO)
        break
    except Exception as e:
        logging.warning(f"MAVLink vehicle connection failed: {e}")
        logging.warning("Retrying...")


drone.wait_heartbeat()
logging.info("Hearbeat received!")

drone.mav.request_data_stream_send(
    drone.target_system,
    drone.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,  # req_stream_id
    1,  # Rate in Hertz
    1  # Start/Stop
)

cam = Camera()
cloud_link = None

now = time.time()
timer_names = ['data_collect', 'data_send', 'take_pic']
last_tss = {tn: now for tn in timer_names}

vehicle = {
    'armed': False,
    'position': None
}

leds.success()


def is_trustable(msg, ids):
    return all([
        msg.get_srcComponent() == ids['component'],
        msg.get_srcSystem() == ids['system']
    ])


def cleanup_msg(link):
    msg = link.recv_msg()
    msg_type = msg and msg.get_type()
    message_is_valid = msg_type and msg_type != 'BAD_DATA'
    return msg if message_is_valid else None


def update_vehicle_state(msg, vehicle):
    if is_trustable(msg, settings.VEHICLE_IDS):
        msg_type = msg.get_type()

        if msg_type == 'HEARTBEAT':
            vehicle['armed'] = bool(msg.base_mode // 128)
            logging.debug(f"(HEARTBEAT) {vehicle}")

        if msg_type == 'GLOBAL_POSITION_INT':
            vehicle['position'] = {
                'lat': float(msg.lat) / 10**7,
                'lon': float(msg.lon) / 10**7,
                'alt': float(msg.alt) / 10**3,
            }
            logging.debug(f"(GLOBAL_POSITION_INT) {vehicle}")

    return vehicle


def create_cloud_link():
    try:
        return create_connection(
            settings.WS_ENDPOINT,
            timeout=settings.WS_TIMEOUT,
            sslopt={"cert_reqs": ssl.CERT_NONE}
        )
    except Exception as e:
        logging.error(f"Cloud link error: {e}")


def send_to_cloud(link, msg):
    if msg.get_type() not in settings.WS_MSG_TYPES:
        return link

    if link is None:
        link = create_cloud_link()

    if link is not None:
        try:
            link.send(msg.to_json())
        except BrokenPipeError:
            logging.error("Broken pipe. Cloud link error")
            link = None

    return link


while True:
    try:

        mav_msg = cleanup_msg(drone)
        if mav_msg is None:
            continue

        vehicle = update_vehicle_state(mav_msg, vehicle)
        cloud_link = send_to_cloud(cloud_link, mav_msg)

        now = time.time()
        elapsed_times = {tn: now - last_tss[tn] for tn in timer_names}

        if elapsed_times['data_collect'] > settings.DATA_COLLECT_TIMESPAN:
            if vehicle['armed'] and vehicle['position']:
                if vehicle['position']['alt'] > settings.DATA_COLLECT_MIN_ALT:
                    collect_data(vehicle['position'])
                    last_tss['data_collect'] = now

        if elapsed_times['data_send'] > settings.MAVLINK_SAMPLES_TIMESPAN:
            package = prepare_data()
            if package:
                pack_len = len(package)
                logging.info(f"Sending data ({pack_len}): {package}")
                if pack_len > 254:
                    logging.warning("MESSAGE TOO LONG TO SEND")
                else:
                    drone.mav.tukano_data_send(package)
                    logging.info("Data sent to ground")
                    tukano_msg = drone.mav.tukano_data_encode(package)
                    cloud_link = send_to_cloud(tukano_msg)

            last_tss['data_send'] = now

        if elapsed_times['take_pic'] > settings.TAKE_PIC_TIMESPAN:
            if vehicle['armed']:
                if vehicle['position']:
                    pic_name = cam.take_pic(gps_data={
                        'lat': vehicle['position']['lat'],
                        'lon': vehicle['position']['lon'],
                        'alt': vehicle['position']['alt']
                    })
                else:
                    pic_name = cam.take_pic()

                last_tss['take_pic'] = now
                logging.info(f"Pic taken '{pic_name}'")

        if vehicle['armed'] and not cam.is_recording:
            vid_name = cam.start_recording()
            logging.info(f"Recording video '{vid_name}'")

        if not vehicle['armed'] and cam.is_recording:
            vid_name = cam.stop_recording()
            logging.info(f"Video recordered '{vid_name}'")

    except Exception as e:
        leds.error()
        logging.error(f"General error happened: {e}")
