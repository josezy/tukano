import os
import logging

os.environ['MAVLINK_DIALECT'] = "mav_tukano"

PROD = False  # Development flag

SLEEPING_TIME = 0.0001
LOGGING_LEVEL = logging.DEBUG  # DEBUG-INFO-WARNING-ERROR-CRITICAL

###############################################################################
# Directory contants
###############################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = f"{BASE_DIR}/data"
PICS_DIR = f"{DATA_DIR}/pics"
VIDEOS_DIR = f"{DATA_DIR}/videos"

###############################################################################
# Connection parameters
###############################################################################

# Aircraft connections
MAVLINK_VEHICLE = (
    {
        # 'device': "/dev/ttyAMA0",  # UART on ARM architectures (RPi1)
        'device': "/dev/ttyS0",  # UART on x86 and x86_64 architectures (RPi3)
        'baud': 57600,
    }
    if PROD else
    {
        'device': "tcp:localhost:5760",  # SITL on local PC
    }
)
MAVLINK_TUKANO = {
    'device': "udp:127.0.0.1:14551",
}
MAVLINK_GROUND = (
    {
        'device': "/dev/ttyUSB0",  # XBee on USB port (RPi)
        'baud': 115200,
    }
    if PROD else
    {
        'device': "udp:127.0.0.1:14552",
    }
)

# Ground connections
MAVLINK_AIRCRAFT = (
    {
        'device': "/dev/ttyUSB0",
        'baud': 115200,
    }
    if PROD else
    {
        'device': "udp:127.0.0.1:14552",  # XBee on USB port (PC)
    }
)
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

# RGB Led for status indication
LED_PINS = {
    'red': 12,
    'green': 16,
    'blue': 20,
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

###############################################################################
# Serial communication for transferring external data
###############################################################################

SERIAL_PARAMS = {
    'port': '/dev/ttyUSB0',  # This must be manually set every time
    'baudrate': 115200
}

###############################################################################
# Websockets parameters
###############################################################################

WS_ENDPOINT = "ws://localhost:8000/flight"
WS_MSG_TYPES = (
    'HEARTBEAT', 'TUKANO_DATA', 'GLOBAL_POSITION_INT'
)
