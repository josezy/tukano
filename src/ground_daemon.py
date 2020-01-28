import json
import time
import logging
import settings

from datetime import datetime
from pymavlink import mavutil
from websocket import create_connection

from util.util import append_json_file


logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=settings.LOGGING_LEVEL
)


while True:
    try:
        aircraft_link = mavutil.mavlink_connection(**settings.MAVLINK_AIRCRAFT)
        logging.info(f"Aircraft at {settings.MAVLINK_AIRCRAFT['device']}")
        break
    except Exception as e:
        logging.warn(e)
        logging.warn("Retrying MAVLink aircraft connection...")

gcs_link = mavutil.mavlink_connection(input=False, **settings.MAVLINK_GCS)
logging.info(f"GCS stablished at {settings.MAVLINK_GCS['device']}")

aircraft_link.wait_heartbeat()
logging.info("Aircraft hearbeat received!")

while True:
    try:
        ws = create_connection(settings.WS_ENDPOINT)
        break
    except Exception as e:
        logging.error(e)
        time.sleep(2)

session_name = datetime.now().strftime("%Y_%m_%d_%H_%M")


def save_to_file(msg):
    data = json.loads(msg.text)
    append_json_file(f"{session_name}.json", data)
    logging.debug(data)


while True:
    m = aircraft_link.recv()
    msgs = aircraft_link.mav.parse_buffer(m)
    if msgs:
        for msg in msgs:
            gcs_link.write(msg.get_msgbuf())

            try:
                if msg.get_type() == "TUKANO_DATA":
                    save_to_file(msg)
                if msg.get_type() in settings.WS_MSG_TYPES:
                    ws.send(msg.to_json())
            except Exception as e:
                logging.error(e)

    m2 = gcs_link.recv()
    aircraft_link.write(m2)

    time.sleep(settings.SLEEPING_TIME)
