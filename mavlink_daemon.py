"""
    Remember to generate MAVLink library with
    mavgen.py --output=venv/lib/python2.7/site-packages/pymavlink/dialects/v10/mav_tukano.py dialects/mav_tukano.xml
    after changing dialects/mav_tukano.xml, otherwise this code may not work
"""

import time
import json
import redis

from src import settings
from src.leds import error, info, success, led_off

from pymavlink import mavutil

while True:
    try:
        vehicle_link = mavutil.mavlink_connection(
            settings.MAVLINK_VEHICLE_ADDRESS
        )
        print("Vehicle connected at {}".format(
            settings.MAVLINK_VEHICLE_ADDRESS
        ))
        success()
        break
    except Exception as e:
        error()
        time.sleep(3)

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

led_off()

while True:

    vehicle_msg = vehicle_link.recv_msg()
    if vehicle_msg and vehicle_msg.get_type() != 'BAD_DATA':
        ground_link.mav.send(vehicle_msg)
        tukano_link.mav.send(vehicle_msg)
        if settings.VERBOSE:
            print(vehicle_msg)

    ground_msg = ground_link.recv_msg()
    if ground_msg and ground_msg.get_type() != 'BAD_DATA':
        vehicle_link.mav.send(ground_msg)
        if settings.VERBOSE:
            print(ground_msg)

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
            info()
            data_text = json.dumps(data)
            data_len = len(data_text)
            if settings.VERBOSE:
                print("Sending data ({}): {}".format(data_len, data_text))
            if data_len > 254:
                print("MESSAGE TOO LONG TO SEND")
                error()
            else:
                ground_link.mav.tukano_data_send(data_text)
                led_off()

        last_t = time.time()

    time.sleep(settings.SLEEPING_TIME)
