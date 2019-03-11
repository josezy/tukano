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

no_vehicle = True

while no_vehicle:
    try:
        vehicle_link = mavutil.mavlink_connection(
            settings.MAVLINK_VEHICLE_ADDRESS
        )
        no_vehicle = False
    except Exception as e:
        print(e)
        print("Retrying MAVLink vehicle connection...")

gcs_link = mavutil.mavlink_connection(
    settings.MAVLINK_GCS_ADDRESS,
    input=False,
)

print("Waiting for vehicle hearbeat")
vehicle_link.wait_heartbeat()
print("Vehicle hearbeat received!")

vehicle_link.logfile_raw = gcs_link
gcs_link.logfile_raw = vehicle_link

redis_queue = redis.Redis(**settings.REDIS_CONF)

last_t = time.time()

while True:

    vehicle_msg = vehicle_link.recv_msg()
    if vehicle_msg and vehicle_msg.get_type() != 'BAD_DATA':
        gcs_link.mav.send(vehicle_msg)

    gcs_msg = gcs_link.recv_msg()
    if gcs_msg and gcs_msg.get_type() != 'BAD_DATA':
        vehicle_link.mav.send(gcs_msg)

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
            gcs_link.mav.statustext_long_send(
                mavutil.mavlink.MAV_SEVERITY_INFO,
                "TUKANO_DATA {}".format(json.dumps(data))
            )
        last_t = time.time()
