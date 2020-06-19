"""
    Remember to update MAVLink dialect with:
    cp dialects/* .venv/lib/python3.7/site-packages/message_definitions/v1.0/
"""

import time
import serial
import logging

import settings

from pymavlink import mavutil


logging.basicConfig(**settings.LOGGING_KWARGS)


def connect_vehicle():
    while True:
        try:
            link = mavutil.mavlink_connection(**settings.MAVLINK_DAEMON)
            logging.info(
                f"Vehicle connected at {settings.MAVLINK_DAEMON['device']}")
            break
        except Exception as e:
            logging.error(f"Vehicle connection error: {e}")
            time.sleep(1)

    return link


vehicle_link = connect_vehicle()

try:
    ground_link = mavutil.mavlink_connection(
        input=False,
        **settings.MAVLINK_GROUND
    )
    logging.info(f"Ground at {settings.MAVLINK_GROUND['device']}")
except serial.SerialException:
    ground_link = None
    logging.warning(f"NO GROUND LINK at {settings.MAVLINK_GROUND}")


tukano_link = mavutil.mavlink_connection(
    input=False,
    **settings.MAVLINK_TUKANO
)
logging.info(f"MAVLink tukano at {settings.MAVLINK_TUKANO['device']}")

logging.info("Waiting for vehicle hearbeat")
vehicle_link.wait_heartbeat()
logging.info("Vehicle hearbeat received!")


while True:

    # From vehicle to ground/tukano
    try:
        vehicle_m = vehicle_link.recv()
    except ConnectionResetError as e:
        logging.error(f"MAVLINK VEHICLE ERROR: {e}")
        vehicle_link = connect_vehicle()
        continue

    vehicle_msgs = vehicle_link.mav.parse_buffer(vehicle_m)
    if vehicle_msgs:
        for vehicle_msg in vehicle_msgs:
            logging.debug(f"(VEHICLE_MSG) {vehicle_msg}")
            if ground_link:
                ground_link.write(vehicle_msg.get_msgbuf())

            if tukano_link:
                tukano_link.write(vehicle_msg.get_msgbuf())

    # From ground to vehicle
    if ground_link:
        ground_m = ground_link.recv()
        ground_msgs = ground_link.mav.parse_buffer(ground_m)
        if ground_msgs:
            for ground_msg in ground_msgs:
                logging.info(f"(GROUND_MSG) {ground_msg}")
                vehicle_link.write(ground_msg.get_msgbuf())

    # From tukano to vehicle
    tukano_m = tukano_link.recv()
    tukano_msgs = tukano_link.mav.parse_buffer(tukano_m)
    if tukano_msgs:
        for tukano_msg in tukano_msgs:
            logging.info(f"(TUKANO_MSG) {tukano_msg}")
            vehicle_link.write(tukano_msg.get_msgbuf())

    time.sleep(settings.SLEEPING_TIME)
