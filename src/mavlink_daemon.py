"""
    Remember to generate MAVLink library with
    mavgen.py --output=.venv/lib/python3.7/site-packages/pymavlink/dialects/v10/mav_tukano.py dialects/mav_tukano.xml
    after changing dialects/mav_tukano.xml, otherwise this code may not work
"""

import time
import serial
import logging

import settings

from pymavlink import mavutil


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
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
        logging.error(f"Vehicle connection error: {e}")
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


while True:

    # From vehicle to ground/tukano
    vehicle_m = vehicle_link.recv()
    vehicle_msgs = vehicle_link.mav.parse_buffer(vehicle_m)
    if vehicle_msgs:
        for vehicle_msg in vehicle_msgs:
            logging.debug("(VEHICLE_MSG) {}".format(vehicle_msg))
            if ground_link:
                ground_link.write(vehicle_msg.get_msgbuf())

            if tukano_link:
                tukano_link.write(vehicle_msg.get_msgbuf())

    # From ground to vehicle/tukano
    if ground_link:
        ground_m = ground_link.recv()
        ground_msgs = ground_link.mav.parse_buffer(ground_m)
        if ground_msgs:
            for ground_msg in ground_msgs:
                logging.debug("(GROUND_MSG) {}".format(ground_msg))
                vehicle_link.write(ground_msg.get_msgbuf())

                if tukano_link:
                    tukano_link.write(ground_msg.get_msgbuf())

    # From tukano to vehicle/ground
    tukano_m = tukano_link.recv()
    tukano_msgs = tukano_link.mav.parse_buffer(tukano_m)
    if tukano_msgs:
        for tukano_msg in tukano_msgs:
            logging.debug("(TUKANO_MSG) {}".format(tukano_msg))
            vehicle_link.write(tukano_msg.get_msgbuf())

            if ground_link:
                ground_link.write(tukano_msg.get_msgbuf())

    time.sleep(settings.SLEEPING_TIME)
