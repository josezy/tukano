"""
    Remember to include custom MAVLink dialect:
    cp dialects/* .venv/lib/python3.7/site-packages/message_definitions/v1.0/
"""

import ssl
import json
import time
import math
import socket
import settings
import logging
import traceback
import websocket
import typing as ty
import serial

from pymavlink import mavutil
from websocket import create_connection

from tasks import collect_data, prepare_data
from actuators import Hook
from util import leds
from timer import Timer


def connect_drone():
    while True:
        try:
            drone = mavutil.mavlink_connection(**settings.MAVLINK_TUKANO)
            break
        except Exception as e:
            logging.warning(f"MAVLink vehicle connection failed: {e}")
            logging.warning("Retrying...")
            time.sleep(1)  # Add delay between retries

    return drone


def init_drone(drone, timeout=None):
    """Initialize drone connection and set up data streams"""
    try:
        heartbeat = drone.wait_heartbeat(timeout=timeout)
        logging.info("Heartbeat received!")
        
        vehicle = {
            'system_id': heartbeat.get_srcSystem(),
            'component_id': heartbeat.get_srcComponent(),
            'armed': False,
            'position': None,
            'battery': None,
        }
        
        # Request data streams
        drone.mav.request_data_stream_send(
            vehicle['system_id'],
            vehicle['component_id'],
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10,  # Rate in Hertz
            1  # Start/Stop
        )
        
        return drone, vehicle
    except Exception as e:
        logging.error(f"Failed to get heartbeat: {e}")
        raise


def reconnect_drone(prev_drone=None):
    """Safely close previous connection if exists and establish a new connection"""
    if prev_drone is not None:
        try:
            prev_drone.close()
        except Exception as e:
            logging.warning(f"Error closing previous connection: {e}")
    
    logging.info("Attempting to reconnect to drone...")
    new_drone = connect_drone()
    
    try:
        return init_drone(new_drone, timeout=5)
    except Exception as e:
        logging.error(f"Failed to initialize drone after reconnection: {e}")
        return reconnect_drone(new_drone)  # Recursive retry if initialization fails


def is_trustable(msg, vehicle):
    return all([
        msg.get_srcSystem() == vehicle['system_id'],
        msg.get_srcComponent() == vehicle['component_id']
    ])


def cleanup_msg(link):
    try:
        msg = link.recv_msg()
        msg_type = msg and msg.get_type()
        message_is_valid = msg_type and msg_type != 'BAD_DATA'
        return msg if message_is_valid else None
    except (serial.serialutil.SerialException, socket.error, OSError, IOError, Exception) as e:
        # This will be caught in the main loop - handle both serial and socket errors
        if isinstance(e, serial.serialutil.SerialException):
            logging.error(f"Serial exception in cleanup_msg: {e}")
        else:
            logging.error(f"Connection error in cleanup_msg: {e}")
        # Check specifically for EOF errors which might not raise exceptions
        if hasattr(link, 'port') and hasattr(link.port, 'file') and link.port.file.closed:
            logging.error("Connection closed or EOF detected")
        raise


def update_vehicle_state(msg, vehicle):
    if is_trustable(msg, vehicle):
        msg_type = msg.get_type()

        if msg_type == 'HEARTBEAT':
            vehicle['armed'] = bool(msg.base_mode & 2**7)
            vehicle['system_id'] = msg.get_srcSystem()
            vehicle['component_id'] = msg.get_srcComponent()

        if msg_type == 'GLOBAL_POSITION_INT':
            vehicle['position'] = {
                'lat': float(msg.lat) / 10**7,
                'lon': float(msg.lon) / 10**7,
                'alt': float(msg.alt) / 10**3,
            }

        if msg_type == "SYS_STATUS":
            vehicle['battery'] = msg.battery_remaining

    return vehicle


def create_cloud_link(endpoint) -> None:
    try:
        logging.info(f"Creating cloud link at {endpoint}")
        link = create_connection(endpoint, **settings.WS_CONNECTION_PARAMS)
        link.settimeout(0)
        logging.info("Connected!")
        return link
    except Exception as e:
        logging.error(f"Cloud link error: {e}")


def mav_data_to_cloud(link, msg) -> None:
    if msg.get_type() not in settings.WS_MAV_MSG_TYPES:
        return

    try:
        link.send(json.dumps({
            'srcSystem': msg.get_srcSystem(),
            'srcComponent': msg.get_srcComponent(),
            **msg.to_dict()
        }))
        if msg.get_type() == "HEARTBEAT":
            logging.debug(f"[MAV DATA TO CLOUD] {msg.to_json()}")
    except (
        BrokenPipeError,
        websocket.WebSocketConnectionClosedException,
        OSError,
    ) as e:
        logging.error(f"[MAV DATA SEND] Cloud link error: {e}")
        link.close()


def mav_data_from_cloud(link):
    mavmsg = None

    try:
        recv_str = link.recv()
        msg = json.loads(recv_str)
        if any([
            'command' in msg,
            'message' in msg,
        ]):
            mavmsg = msg
            logging.debug(f"[MAV DATA FROM CLOUD] {recv_str}")
    except (
        BrokenPipeError,
        websocket.WebSocketConnectionClosedException,
        ConnectionResetError,
    ) as e:
        logging.error(f"[MAV DATA RECV] Broken pipe. Cloud link error: {e}")

    except (
        BlockingIOError,
        json.JSONDecodeError,
        ssl.SSLWantReadError,
        OSError,
    ):
        pass

    return mavmsg


def command_to_drone(drone, command: ty.Dict[str, ty.Any]) -> ty.NoReturn:
    mavcmd = command.get('command')
    target_system = command.get('target_system')
    target_component = command.get('target_component')
    params = command.get('params')
    params = [params.get(f"param{i+1}", math.nan) for i in range(7)]
        
    drone.mav.command_long_send(
        target_system,
        target_component,
        getattr(mavutil.mavlink, mavcmd),
        0,  # confirmation (not used yet)
        *params
    )
    logging.debug(f"[COMMAND TO DRONE] Delivered command {mavcmd} with params: {params}")


def message_to_drone(drone, message: ty.Dict[str, ty.Any]) -> ty.NoReturn:
    mavmsg = message.get('message')
    params = message.get('params')
    args = [
        val.encode() if type(val) == str else val
        for val in params.values()
    ]
    mavmsg_send = getattr(drone.mav, f"{mavmsg.lower()}_send")
    mavmsg_send(*args)
    logging.debug(f"[MESSAGE TO DRONE] Delivered message {mavmsg} with args: {args}")


def tukano_command(command: ty.Dict[str, ty.Any]) -> ty.NoReturn:
    tukano_cmd = command.get('command')
    # params = command.get('params')
    if tukano_cmd == 'TUKANO_RELEASE_HOOK':
        hook.release()


# =============[From here to down hell]================

logging.basicConfig(**settings.LOGGING_KWARGS)
print(f"Logging level: {settings.LOGGING_KWARGS}")
logging.info(f"Initialising vehicle at {settings.MAVLINK_TUKANO['device']}")

leds.led_on('red')
drone = connect_drone()
drone, vehicle = init_drone(drone)

hook = Hook()
timer = Timer({
    'collect_data': settings.DATA_COLLECT_TIMESPAN,
    'send_data': settings.MAVLINK_SAMPLES_TIMESPAN,
    'take_pic': settings.TAKE_PIC_TIMESPAN,
})

if any((settings.TAKE_PIC, settings.RECORD)):
    from camera import Camera
    cam = Camera()

cloud_mav_link = create_cloud_link(settings.WS_MAV_ENDPOINT)
cloud_last_heartbeat = time.time()

leds.led_on('blue')
red_on = False
while True:
    time.sleep(settings.SLEEPING_TIME)

    try:
        try:
            mav_msg = cleanup_msg(drone)
            # Check for EOF on TCP socket which might be logged but not raise an exception
            if hasattr(drone, 'port') and hasattr(drone.port, 'file') and drone.port.file.closed:
                raise Exception("EOF on TCP socket detected")
                
            if mav_msg is not None:
                vehicle = update_vehicle_state(mav_msg, vehicle)
        except (serial.serialutil.SerialException, socket.error, OSError, IOError, Exception) as e:
            logging.error(f"Connection lost: {e}")
            leds.led_on('red')
            # Attempt to reconnect
            drone, vehicle = reconnect_drone(drone)
            leds.led_on('blue')
            # Skip the rest of this iteration
            continue

        if cloud_mav_link is not None and cloud_mav_link.connected:
            if mav_msg is not None:
                mav_data_to_cloud(cloud_mav_link, mav_msg)

            cloud_data = mav_data_from_cloud(cloud_mav_link)
            if cloud_data and 'command' in cloud_data:
                if cloud_data['command'].startswith('TUKANO'):
                    tukano_command(cloud_data)
                else:
                    command_to_drone(drone, cloud_data)

            if cloud_data and 'message' in cloud_data:
                if cloud_data.get('message') == 'HEARTBEAT':
                    cloud_last_heartbeat = time.time()
                    leds.led_on('green')
                    red_on = False

                message_to_drone(drone, cloud_data)

        else:
            logging.error("No cloud_mav_link, recreating...")
            cloud_mav_link = create_cloud_link(settings.WS_MAV_ENDPOINT)
            time.sleep(1)

        if time.time() - cloud_last_heartbeat > 2 and not red_on:
            leds.led_on('red')
            red_on = True

        # =================[ Tasks ]=================
        timer.update_elapsed_times()

        if settings.DATA_COLLECT:
            if timer.time_to('collect_data'):
                if vehicle['position']:
                    veh_alt = vehicle['position']['alt']
                    if veh_alt > settings.DATA_COLLECT_MIN_ALT:
                        collect_data(vehicle['position'])

            if timer.time_to('send_data'):
                package = prepare_data()
                if package:
                    pack_len = len(package)
                    logging.debug(f"Sending data ({pack_len}): {package}")
                    if pack_len > 1048:
                        logging.warning("Message too long: Truncating...")

                    # drone.mav.tukano_data_send(package)
                    # logging.info("Data sent to ground")
                    tukano_msg = drone.mav.tukano_data_encode(package)
                    mav_data_to_cloud(cloud_mav_link, tukano_msg)
                    logging.info("Data sent to cloud")

        if settings.TAKE_PIC and timer.time_to('take_pic'):
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

        if settings.RECORD:
            if vehicle['armed'] and not cam.is_recording:
                vid_name = cam.start_recording()
                logging.info(f"Recording video '{vid_name}'")

            if not vehicle['armed'] and cam.is_recording:
                vid_name = cam.stop_recording()
                logging.info(f"Video recordered '{vid_name}'")

    except Exception as e:
        leds.led_on('red')
        logging.error(f"Main loop error: {e}")
        traceback.print_exc()
