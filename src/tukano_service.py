import ssl
import json
import time
import settings
import logging
import traceback
import websocket

import timer as Timer

from pymavlink import mavutil
from websocket import create_connection

from tasks import collect_data, prepare_data
from camera import Camera
from actuators import Hook
from util import leds


def logging_config():
    logging.basicConfig(
        format=settings.LOGGING_FORMAT,
        level=settings.LOGGING_LEVEL
    )
    logging.info(f"Initialising vehicle at {settings.MAVLINK_VEHICLE['device']}")


def get_drone():
    while True:
        try:
            drone =  mavutil.mavlink_connection(**settings.MAVLINK_VEHICLE)
            break
        except Exception as e:
            logging.warning(f"MAVLink vehicle connection failed: {e}")
            logging.warning("Retrying...")

    heartbeat = drone.wait_heartbeat()
    logging.info("Hearbeat received!")

    system_id = heartbeat.get_srcSystem()
    component_id = heartbeat.get_srcComponent()

    drone.mav.request_data_stream_send(
        system_id,
        component_id,
        mavutil.mavlink.MAV_DATA_STREAM_ALL,  # req_stream_id
        1,  # Rate in Hertz
        1  # Start/Stop
    )

    return drone


def get_vehicle():
    return {
        'armed': False,
        'position': None,
        'battery' : None
    }


def is_trustable(msg, heartbeat):
    system_id = heartbeat.get_srcSystem()
    component_id = heartbeat.get_srcComponent()

    return all([
        msg.get_srcSystem() == system_id,
        msg.get_srcComponent() == component_id
    ])


def cleanup_msg(link):
    msg = link.recv_msg()
    msg_type = msg and msg.get_type()
    message_is_valid = msg_type and msg_type != 'BAD_DATA'
    return msg if message_is_valid else None


def update_vehicle_state(msg, vehicle, heartbeat):
    if is_trustable(msg, heartbeat):
        msg_type = msg.get_type()

        if msg_type == 'HEARTBEAT':
            vehicle['armed'] = bool(msg.base_mode // 2**7)
            logging.debug(f"(HEARTBEAT) {vehicle}")

        if msg_type == 'GLOBAL_POSITION_INT':
            vehicle['position'] = {
                'lat': float(msg.lat) / 10**7,
                'lon': float(msg.lon) / 10**7,
                'alt': float(msg.alt) / 10**3,
            }
            logging.debug(f"(GLOBAL_POSITION_INT) {vehicle}")

        if msg_type == "SYS_STATUS":
            vehicle['battery'] = msg.battery_remaining
    return vehicle


def create_cloud_link():
    try:
        return create_connection(
            settings.WS_ENDPOINT,
            **settings.WS_CONNECTION_PARAMS
        )
    except Exception as e:
        logging.error(f"Cloud link error: {e}")


def send_to_cloud(link, msg):
    if msg.get_type() not in settings.WS_MSG_TYPES:
        return

    try:
        link.send(json.dumps({
            'srcSystem': msg.get_srcSystem(),
            'srcComponent': msg.get_srcComponent(),
            **msg.to_dict()
        }))
    except (BrokenPipeError, websocket.WebSocketConnectionClosedException):
        logging.error("[SEND] Broken pipe. Cloud link error")


def data_from_cloud(link):
    mavmsg = None

    try:
        link.settimeout(0)
        msg = json.loads(link.recv())
        if any([
            'command' in msg,
            'message' in msg,
        ]):
            mavmsg = msg
    except (BrokenPipeError, websocket.WebSocketConnectionClosedException):
        logging.error("[RECV] Broken pipe. Cloud link error")
    except (BlockingIOError, json.JSONDecodeError, ssl.SSLWantReadError):
        pass

    return mavmsg


def command_to_drone(command):
    mav_cmd = command.pop('command')
    target_system = command.pop('target_system')
    target_component = command.pop('target_component')
    params = [command.get(f"param{i+1}", 0) for i in range(7)]
    drone.mav.command_long_send(
        target_system,
        target_component,
        getattr(mavutil.mavlink, mav_cmd),
        0,  # confirmation (not used yet)
        *params
    )


def process_message(message):
    mavmsg = message.pop('message')
    args = message.values()
    mavmsg_send = getattr(drone.mav, f"{mavmsg.lower()}_send")
    mavmsg_send(*args)


def tukano_command(command):
    tukano_cmd = command.pop('command')
    # params = command
    if tukano_cmd == 'TUKANO_RELEASE_HOOK':
        hook.release()

leds.info()
logging_config()

drone = get_drone()
heartbeat = drone.wait_heartbeat()
vehicle = get_vehicle()

timer = Timer.Timer(['collect_data', 'send_data', 'take_pic'])
hook = Hook()
cam = Camera()
cloud_link = create_cloud_link()
leds.success()

while True:
    time.sleep(settings.SLEEPING_TIME)

    try:

        mav_msg = cleanup_msg(drone)
        if mav_msg is None:
            continue

        vehicle = update_vehicle_state(mav_msg, vehicle, heartbeat)

        if cloud_link is None or not cloud_link.connected:
            cloud_link = create_cloud_link()

        if cloud_link is not None and cloud_link.connected:
            send_to_cloud(cloud_link, mav_msg)

            cloud_data = data_from_cloud(cloud_link)
            if cloud_data and 'command' in cloud_data:
                if cloud_data['command'].startswith('TUKANO'):
                    tukano_command(cloud_data)
                else:
                    command_to_drone(cloud_data)

            if cloud_data and 'message' in cloud_data:
                process_message(cloud_data)

        # Tasks
        now = time.time()
        elapsed_times = {tn: now - timer.last_tss[tn] for tn in timer.timer_names}

        if timer.can_collect_data():  
            if vehicle['armed'] and vehicle['position']:
                if vehicle['position']['alt'] > settings.DATA_COLLECT_MIN_ALT:
                    collect_data(vehicle['position'])

        if timer.can_send_data():
            package = prepare_data()
            if package:
                pack_len = len(package)
                logging.debug(f"Sending data ({pack_len}): {package}")
                if pack_len > 1048:
                    logging.warning("Message too long: Truncating...")

                # drone.mav.tukano_data_send(package)
                # logging.info("Data sent to ground")
                tukano_msg = drone.mav.tukano_data_encode(package)
                send_to_cloud(cloud_link, tukano_msg)
                logging.info("Data sent to cloud")

        if timer.can_take_pic():
            if vehicle['armed'] and vehicle['battery'] > 30:
                if vehicle['position']:
                    pic_name = cam.take_pic(gps_data={
                        'lat': vehicle['position']['lat'],
                        'lon': vehicle['position']['lon'],
                        'alt': vehicle['position']['alt']
                    })
                else:
                    pic_name = cam.take_pic()

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
        traceback.print_exc()
