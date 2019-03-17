import json

from src import settings
from src.util import append_json_file

from pymavlink import mavutil

while True:
    try:
        aircraft_link = mavutil.mavlink_connection(
            settings.MAVLINK_AIRCRAFT_ADDRESS
        )
        print("Aircraft connected at {}".format(settings.MAVLINK_AIRCRAFT_ADDRESS))
        break
    except Exception as e:
        print(e)
        print("Retrying MAVLink aircraft connection...")

gcs_link = mavutil.mavlink_connection(
    settings.MAVLINK_GCS_ADDRESS,
    input=False,
)
print("GCS stablished at {}".format(settings.MAVLINK_GCS_ADDRESS))

aircraft_link.wait_heartbeat()
print("Aircraft hearbeat received!")


def incoming_msg(msg):
    data = json.loads(msg.text)
    append_json_file("data_collected.json", data)
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
