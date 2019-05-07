"""
    Remember to generate MAVLink library with
    mavgen.py --output=venv/lib/python2.7/site-packages/pymavlink/dialects/v10/mav_tukano.py dialects/mav_tukano.xml
    after changing dialects/mav_tukano.xml, otherwise this code may not work
"""

import time
import json
import redis
import settings

from pymavlink import mavutil

from util.leds import error, info, success, led_off

while True:
    try:
        vehicle_link = mavutil.mavlink_connection(**settings.MAVLINK_VEHICLE)
        print("Vehicle connected at {}".format(
            settings.MAVLINK_VEHICLE['device']
        ))
        success()
        break
    except Exception as e:
        error()
        time.sleep(3)

ground_link = mavutil.mavlink_connection(
    input=False,
    **settings.MAVLINK_GROUND
)
print("Ground at {}".format(settings.MAVLINK_GROUND['device']))

tukano_link = mavutil.mavlink_connection(
    input=False,
    **settings.MAVLINK_TUKANO
)
print("MAVLink tukano at {}".format(settings.MAVLINK_TUKANO['device']))

print("Waiting for vehicle hearbeat")
vehicle_link.wait_heartbeat()
print("Vehicle hearbeat received!")

vehicle_link.logfile_raw = ground_link
ground_link.logfile_raw = vehicle_link
tukano_link.logfile_raw = vehicle_link

try:
    redis_queue = redis.Redis(**settings.REDIS_CONF)
except Exception as e:
    error()
    raise e

last_t = time.time()

led_off()

while True:

    vehicle_msg = vehicle_link.recv_msg()
    if vehicle_msg and vehicle_msg.get_type() != 'BAD_DATA':
        ground_link.mav.send(vehicle_msg)
        tukano_link.mav.send(vehicle_msg)
        if settings.VERBOSE_LEVEL <= 0:
            print(vehicle_msg)

    ground_msg = ground_link.recv_msg()
    if ground_msg and ground_msg.get_type() != 'BAD_DATA':
        vehicle_link.mav.send(ground_msg)
        if settings.VERBOSE_LEVEL <= 0:
            print(ground_msg)

    if time.time() - last_t > settings.MAVLINK_SAMPLES_TIMESPAN:
        samples = 0
        data = []
        while samples < settings.MAX_SAMPLES_PER_MAVLINK_MESSAGE:
            sample = redis_queue.rpop('TUKANO_DATA')
            if not sample:
                break

            data.append(json.loads(sample))
            samples += 1

        if data:
            info()
            data_text = json.dumps(data)
            data_len = len(data_text)
            if settings.VERBOSE_LEVEL <= 1:
                print("Sending data ({}): {}".format(data_len, data_text))
            if data_len > 254:
                print("MESSAGE TOO LONG TO SEND")
                error()
            else:
                ground_link.mav.tukano_data_send(data_text)
                led_off()

        last_t = time.time()

    time.sleep(settings.SLEEPING_TIME)
