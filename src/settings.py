import os
import logging

os.environ['MAVLINK_DIALECT'] = "mav_tukano"

SLEEPING_TIME = 0.000001
LOGGING_LEVEL = logging.DEBUG  # DEBUG-INFO-WARNING-ERROR-CRITICAL

###############################################################################
# Directory contants
###############################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = "{}/data".format(BASE_DIR)
PICS_DIR = "{}/pics".format(DATA_DIR)
VIDEOS_DIR = "{}/videos".format(DATA_DIR)

###############################################################################
# Connection parameters
###############################################################################

# Aircraft connections
MAVLINK_VEHICLE = {
    'device': "tcp:localhost:5760",  # SITL on local PC
    # 'device': "tcp:192.168.1.79:5760",  # SITL on remote PC
    # 'device': "/dev/ttyAMA0",  # UART on ARM architectures (RPi1)
    # 'device': "/dev/ttyS0",  # UART on x86 and x86_64 architectures (RPi3)
    # 'baud': 57600,
}
MAVLINK_TUKANO = {
    'device': "udp:127.0.0.1:14551",
}
MAVLINK_GROUND = {
    # 'device': "/dev/ttyUSB0",
    'device': "udp:127.0.0.1:14552",
    # 'baud': 115200,
}

# Ground connections
MAVLINK_AIRCRAFT = {
    # 'device': "/dev/ttyUSB0",
    'device': "udp:127.0.0.1:14552",
    # 'baud': 115200,
}
MAVLINK_GCS = {
    'device': "udp:127.0.0.1:14550",
}

VEHICLE_IDS = {
    'component': 1,
    'system': 1
}

###############################################################################
# External hardware pins
###############################################################################

# !!!!!! BE SURE TO NEVER REPEAT PINS!!!!!!

# RGB Led for status indication
LED_PINS = {
    'red': 12,
    'green': 16,
    'blue': 20,
}

# AM2302 Temperature, Humidity sensor
AM2302_PINS = {
    'out': 4,
}

# BMP183 Temperature, Pressure sensor
BMP183_PINS = {
    'sck': 5,
    'sdo': 6,
    'sdi': 13,
    'cs': 26,
}

###############################################################################
# Flight tasks parameters
###############################################################################

DATA_COLLECT_MIN_ALT = 10               # Collect data above N meters
DATA_COLLECT_TIMESPAN = 0.4             # Collect data every Z seconds

TAKE_PIC_TIMESPAN = 1                   # Take picture every Z seconds

MAX_SAMPLES_PER_MAVLINK_MESSAGE = 1     # Samples to send over 1 mav msg
MAVLINK_SAMPLES_TIMESPAN = 0.4          # Time between custom mavlink messages

RECORD_START_ALT = 12                   # Start recording video above N meters
RECORD_STOP_ALT = 8                     # Spot recording video below N meters

###############################################################################
# Redis config
###############################################################################
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 2

REDIS_CONF = {'host': REDIS_HOST, 'port': REDIS_PORT, 'db': REDIS_DB}

# CELERY_BROKER = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)
