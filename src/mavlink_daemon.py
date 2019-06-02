"""
    Remember to generate MAVLink library with
    mavgen.py --output=venv/lib/python2.7/site-packages/pymavlink/dialects/v10/mav_tukano.py dialects/mav_tukano.xml
    after changing dialects/mav_tukano.xml, otherwise this code may not work
"""

import time
import json
import redis
import serial
import logging

import settings

from pymavlink import mavutil


logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=settings.LOGGING_LEVEL
)

while True:
    try:
        vehicle_link = mavutil.mavlink_connection(**settings.MAVLINK_VEHICLE)
        logging.info("Vehicle connected at {}".format(
            settings.MAVLINK_VEHICLE['device']
        ))
        break
    except Exception as e:
        time.sleep(3)


try:
    ground_link = mavutil.mavlink_connection(
        input=False,
        **settings.MAVLINK_GROUND
    )
    logging.info("Ground at {}".format(settings.MAVLINK_GROUND['device']))
except serial.SerialException:
    ground_link = None
    logging.warning("NO GROUND LINK at {}".format(settings.MAVLINK_GROUND))


tukano_link = mavutil.mavlink_connection(
    input=False,
    **settings.MAVLINK_TUKANO
)
logging.info("MAVLink tukano at {}".format(settings.MAVLINK_TUKANO['device']))

logging.info("Waiting for vehicle hearbeat")
vehicle_link.wait_heartbeat()
logging.info("Vehicle hearbeat received!")

if ground_link:
    vehicle_link.logfile_raw = ground_link
    ground_link.logfile_raw = vehicle_link

tukano_link.logfile_raw = vehicle_link

try:
    redis_queue = redis.Redis(**settings.REDIS_CONF)
except Exception as e:
    raise e

last_t = time.time()


while True:

    vehicle_msg = vehicle_link.recv_msg()
    if vehicle_msg and vehicle_msg.get_type() != 'BAD_DATA':
        if ground_link:
            ground_link.mav.send(vehicle_msg)

        tukano_link.mav.send(vehicle_msg)
        if settings.VERBOSE_LEVEL <= 0:
            print(vehicle_msg)

    ground_msg = ground_link and ground_link.recv_msg()
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
            data_text = json.dumps(data)
            data_len = len(data_text)
            logging.info("Sending data ({}): {}".format(data_len, data_text))
            if data_len > 254:
                logging.warning("MESSAGE TOO LONG TO SEND")
            else:
                ground_link.mav.tukano_data_send(data_text)

        last_t = time.time()

    time.sleep(settings.SLEEPING_TIME)
