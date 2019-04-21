import json
import time
import settings

from datetime import datetime
from pymavlink import mavutil

from util.util import append_json_file

while True:
    try:
        aircraft_link = mavutil.mavlink_connection(**settings.MAVLINK_AIRCRAFT)
        print("Aircraft at {}".format(settings.MAVLINK_AIRCRAFT['device']))
        break
    except Exception as e:
        print(e)
        print("Retrying MAVLink aircraft connection...")

gcs_link = mavutil.mavlink_connection(input=False, **settings.MAVLINK_GCS)
print("GCS stablished at {}".format(settings.MAVLINK_GCS['device']))

aircraft_link.wait_heartbeat()
print("Aircraft hearbeat received!")


session_name = datetime.now().strftime("%Y_%m_%d_%H_%M")


def incoming_msg(msg):
    data = json.loads(msg.text)
    append_json_file("{}.json".format(session_name), data)
    if settings.VERBOSE:
        print(data)


while True:
    m = aircraft_link.recv()
    msgs = aircraft_link.mav.parse_buffer(m)
    if msgs:
        for msg in msgs:
            gcs_link.write(msg.get_msgbuf())

            try:
                if msg.get_type() == "TUKANO_DATA":
                    incoming_msg(msg)
            except Exception as e:
                print(e)

    m2 = gcs_link.recv()
    aircraft_link.write(m2)

    time.sleep(settings.SLEEPING_TIME)
