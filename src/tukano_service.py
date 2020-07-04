import ssl
import json
import time
import asyncio
import settings
import logging
import traceback
import websocket

from pymavlink import mavutil
from websocket import create_connection

from tasks import collect_data, prepare_data, pack_frame
from camera import Camera
from actuators import Hook
from util import leds
from timer import Timer


logging.basicConfig(**settings.LOGGING_KWARGS)
logging.info(f"Initialising vehicle at {settings.MAVLINK_TUKANO['device']}")


def init_drone():
    while True:
        try:
            drone = mavutil.mavlink_connection(**settings.MAVLINK_TUKANO)
            break
        except Exception as e:
            logging.warning(f"MAVLink vehicle connection failed: {e}")
            logging.warning("Retrying...")

    return drone


def is_trustable(msg, vehicle):
    return all([
        msg.get_srcSystem() == vehicle['system_id'],
        msg.get_srcComponent() == vehicle['component_id']
    ])


def cleanup_msg(link):
    msg = link.recv_msg()
    msg_type = msg and msg.get_type()
    message_is_valid = msg_type and msg_type != 'BAD_DATA'
    return msg if message_is_valid else None


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

        logging.debug(f"({msg_type}) {vehicle}")
    return vehicle


def create_cloud_link(endpoint):
    try:
        print(f"Creating cloud link at {endpoint}", flush=True)
        return create_connection(endpoint, **settings.WS_CONNECTION_PARAMS)
    except Exception as e:
        logging.error(f"Cloud link error: {e}")


def mavmsg_to_cloud(link, msg):
    if msg.get_type() not in settings.WS_MAV_MSG_TYPES:
        return

    try:
        link.send(json.dumps({
            'srcSystem': msg.get_srcSystem(),
            'srcComponent': msg.get_srcComponent(),
            **msg.to_dict()
        }))
    except (
        BrokenPipeError,
        websocket.WebSocketConnectionClosedException,
    ) as e:
        logging.error(f"[MAV DATA SEND] Broken pipe. Cloud link error: {e}")

    except OSError:
        pass


def mav_data_from_cloud(link):
    mavmsg = None

    try:
        link.settimeout(0)
        msg = json.loads(link.recv())
        if any([
            'command' in msg,
            'message' in msg,
        ]):
            mavmsg = msg
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


async def frame_to_cloud(link, cam):
    try:
        frame = cam.grab_frame()
        packed_frame = pack_frame(frame)
        link.send(packed_frame)
    except (BrokenPipeError, websocket.WebSocketConnectionClosedException):
        logging.error("[FRAME SEND] Broken pipe. Cloud link error")
        import ipdb; ipdb.set_trace()


def command_to_drone(command):
    mav_cmd = command.get('command')
    target_system = command.get('target_system')
    target_component = command.get('target_component')
    params = command.get('params')
    params = [params.get(f"param{i+1}", 0) for i in range(7)]
    drone.mav.command_long_send(
        target_system,
        target_component,
        getattr(mavutil.mavlink, mav_cmd),
        0,  # confirmation (not used yet)
        *params
    )


def process_message(message):
    mavmsg = message.get('message')
    params = message.get('params')
    args = params.values()
    mavmsg_send = getattr(drone.mav, f"{mavmsg.lower()}_send")
    mavmsg_send(*args)


def tukano_command(command):
    tukano_cmd = command.get('command')
    # params = command.get('params')
    if tukano_cmd == 'TUKANO_RELEASE_HOOK':
        hook.release()


leds.info()
drone = init_drone()
heartbeat = drone.wait_heartbeat()

logging.info("Hearbeat received!")

vehicle = {
    'system_id': heartbeat.get_srcSystem(),
    'component_id': heartbeat.get_srcComponent(),
    'armed': False,
    'position': None,
    'battery': None
}

drone.mav.request_data_stream_send(
    vehicle['system_id'],
    vehicle['component_id'],
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    1,  # Rate in Hertz
    1  # Start/Stop
)

timer = Timer({
    'collect_data': settings.DATA_COLLECT_TIMESPAN,
    'send_data': settings.MAVLINK_SAMPLES_TIMESPAN,
    'take_pic': settings.TAKE_PIC_TIMESPAN,
    'send_frame': 1 / settings.STREAM_VIDEO_FPS,
})
hook = Hook()
cam = Camera()
cloud_mav_link = create_cloud_link(settings.WS_MAV_ENDPOINT)
cloud_video_link = create_cloud_link(settings.WS_VIDEO_ENDPOINT)
leds.success()

while True:
    time.sleep(settings.SLEEPING_TIME)

    try:

        mav_msg = cleanup_msg(drone)
        if mav_msg is None:
            continue

        vehicle = update_vehicle_state(mav_msg, vehicle)

        if cloud_mav_link is None or not cloud_mav_link.connected:
            print("no cloud_mav_link", flush=True)
            cloud_mav_link = create_cloud_link(settings.WS_MAV_ENDPOINT)

        if cloud_video_link is None or not cloud_video_link.connected:
            print("no cloud_video_link", flush=True)
            cloud_video_link = create_cloud_link(settings.WS_VIDEO_ENDPOINT)

        if cloud_mav_link is not None and cloud_mav_link.connected:
            mavmsg_to_cloud(cloud_mav_link, mav_msg)

            cloud_data = mav_data_from_cloud(cloud_mav_link)
            if cloud_data and 'command' in cloud_data:
                if cloud_data['command'].startswith('TUKANO'):
                    tukano_command(cloud_data)
                else:
                    command_to_drone(cloud_data)

            if cloud_data and 'message' in cloud_data:
                process_message(cloud_data)
        else:
            time.sleep(1)
            raise Exception('No cloud_mav_link')

        # Tasks
        timer.update_elapsed_times()

        if settings.DATA_COLLECT:
            if timer.time_to('collect_data'):
                if vehicle['armed'] and vehicle['position']:
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
                    mavmsg_to_cloud(cloud_mav_link, tukano_msg)
                    logging.info("Data sent to cloud")

        if timer.time_to('take_pic') and settings.TAKE_PIC:
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

        if settings.STREAM_VIDEO:
            if timer.time_to('send_frame'):
                print("sending frame...", flush=True)
                if cloud_video_link is not None and cloud_video_link.connected:
                    frame_to_cloud(cloud_video_link, cam)

        if settings.RECORD:
            if vehicle['armed'] and not cam.is_recording:
                vid_name = cam.start_recording()
                logging.info(f"Recording video '{vid_name}'")

            if not vehicle['armed'] and cam.is_recording:
                vid_name = cam.stop_recording()
                logging.info(f"Video recordered '{vid_name}'")

    except Exception as e:
        leds.error()
        logging.error(f"Main loop error: {e}")
        traceback.print_exc()
