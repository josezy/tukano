"""
    Remember to generate MAVLink library with
    mavgen.py --wire-protocol=2.0 --output=venv/lib/python2.7/site-packages/pymavlink/dialects/v10/mav_tukano.py dialects/mav_tukano.xml
    after changing dialects/mav_tukano.xml, otherwise this code may not work
"""

import time
import json
import redis

from src import settings

from pymavlink import mavutil

while True:
    try:
        vehicle_link = mavutil.mavlink_connection(
            settings.MAVLINK_VEHICLE_ADDRESS
        )
        print("Vehicle connected at {}".format(
            settings.MAVLINK_VEHICLE_ADDRESS
        ))
        break
    except Exception as e:
        print(e)
        print("Retrying MAVLink vehicle connection...")

ground_link = mavutil.mavlink_connection(
    settings.MAVLINK_GROUND_ADDRESS,
    input=False,
)
print("Ground at {}".format(settings.MAVLINK_GROUND_ADDRESS))

tukano_link = mavutil.mavlink_connection(
    settings.MAVLINK_TUKANO_ADDRESS,
    input=False,
)
print("MAVLink tukano at {}".format(settings.MAVLINK_TUKANO_ADDRESS))

print("Waiting for vehicle hearbeat")
vehicle_link.wait_heartbeat()
print("Vehicle hearbeat received!")

vehicle_link.logfile_raw = ground_link
ground_link.logfile_raw = vehicle_link
tukano_link.logfile_raw = vehicle_link

redis_queue = redis.Redis(**settings.REDIS_CONF)

last_t = time.time()

while True:

    vehicle_msg = vehicle_link.recv_msg()
    if vehicle_msg and vehicle_msg.get_type() != 'BAD_DATA':
        # print(vehicle_msg)
        ground_link.mav.send(vehicle_msg)
        tukano_link.mav.send(vehicle_msg)

    ground_msg = ground_link.recv_msg()
    if ground_msg and ground_msg.get_type() != 'BAD_DATA':
        # print(ground_msg)
        vehicle_link.mav.send(ground_msg)

    if time.time() - last_t > settings.MAVLINK_SAMPLES_TIMESPAN:
        samples = 0
        data = []
        while samples < settings.MAX_SAMPLES_PER_MAVLINK_MESSAGE:
            sample = redis_queue.rpop('TUKANO_DATA')
            if not sample:
                break

            data.append(sample)
            samples += 1

        if data:
            ground_link.mav.statustext_send(
                mavutil.mavlink.MAV_SEVERITY_INFO,
                "TUKANO_DATA {}".format(json.dumps(data))
            )
        last_t = time.time()
