import os
import ssl
import logging

os.environ['MAVLINK_DIALECT'] = "mav_tukano"

PROD = os.environ.get('TUKANO_ENV', 'DEV') == "PROD"  # Development flag
print(f"Working on {'production' if PROD else 'development'}")

PLATE = "00000000"  # Unique 8 digit HEX plate to identify drone on ikaro

SLEEPING_TIME = 0.0001
LOGGING_KWARGS = {
    'level': logging.INFO,  # DEBUG-INFO-WARNING-ERROR-CRITICAL
    'format': '[%(levelname)s] %(asctime)s: %(message)s'
}

###############################################################################
# Paths
###############################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = f"{BASE_DIR}/data"
PICS_DIR = f"{DATA_DIR}/pics"
VIDEOS_DIR = f"{DATA_DIR}/videos"
LOGS_DIR = f"{DATA_DIR}/logs"

###############################################################################
# Connection parameters
###############################################################################

# Aircraft connections
# MAVLINK_DAEMON = (
#     {
#         # 'device': "/dev/ttyAMA0",  # UART on ARM architectures (RPi1)
#         'device': "/dev/ttyS0",  # UART on x86 and x86_64 architectures (RPi3)
#         'baud': 57600,
#     }
#     if PROD else
#     {
#         'device': "tcp:localhost:5760",  # dronekit-sitl on local PC
#         # 'device': "udp:127.0.0.1:14540",  # px4_sitl on local PC
#     }
# )
MAVLINK_TUKANO = (
    {
        'device': "/dev/ttyS0",  # UART on x86 and x86_64 architectures (RPi3)
        'baud': 57600,
    }
    if PROD else
    {
        'device': "tcp:localhost:5760",
    }
)
# MAVLINK_GROUND = (
#     {
#         'device': "/dev/ttyUSB0",  # XBee on USB port (RPi)
#         'baud': 115200,
#     }
#     if PROD else
#     {
#         'device': "udp:127.0.0.1:14552",
#     }
# )

# Ground connections
# MAVLINK_AIRCRAFT = (
#     {
#         'device': "/dev/ttyUSB0",  # XBee on USB port (PC)
#         'baud': 115200,
#     }
#     if PROD else
#     {
#         'device': "udp:127.0.0.1:14552",
#     }
# )
# MAVLINK_GCS = {
#     'device': "udp:127.0.0.1:14550",
# }

###############################################################################
# External hardware pins
###############################################################################

# RGB Led for status indication
LED_PINS = {
    'red': 12,
    'green': 16,
    'blue': 20,
}

# Hook trigger
HOOK = {
    'trigger': 26
}

###############################################################################
# Flight tasks parameters
###############################################################################

DATA_COLLECT = False                    # Whether to collect and send data
DATA_COLLECT_MIN_ALT = 10               # Collect data above N meters
DATA_COLLECT_TIMESPAN = 2               # Collect data every Z seconds

TAKE_PIC = False                        # Whether to take pics
TAKE_PIC_TIMESPAN = 1                   # Take picture every Z seconds

MAX_SAMPLES_PER_MAVLINK_MESSAGE = 1     # Samples to send over 1 mav msg
MAVLINK_SAMPLES_TIMESPAN = 0.4          # Time between custom mavlink messages

RECORD = False                          # Whether to record
RECORD_START_ALT = 12                   # Start recording video above N meters
RECORD_STOP_ALT = 8                     # Spot recording video below N meters

STREAM_VIDEO = False                    # Whether to stream
STREAM_VIDEO_FPS = 24                   # Stream video FPS
STREAM_VIDEO_JPEG_QUALITY = 50          # Stream video quality

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

WS_CONNECTION_PARAMS = (
    {'sslopt': {"cert_reqs": ssl.CERT_NONE}} if PROD else {}
)

# WebSocket for mavlink

WS_MAV_ENDPOINT = (
    f"wss://icaro.tucanoar.com/mavlink?plate={PLATE}"
    if PROD else
    f"ws://localhost:8000/mavlink?plate={PLATE}"
)

WS_MAV_MSG_TYPES = (
    'HEARTBEAT', 'TUKANO_DATA', 'GLOBAL_POSITION_INT', 'SYS_STATUS', 'VFR_HUD',
    'GPS_RAW_INT', 'COMMAND_ACK', 'ATTITUDE', 'STATUSTEXT', 'MISSION_COUNT',
    'MISSION_ITEM'
)

# WebSocket for video

WS_VIDEO_ENDPOINT = (
    "wss://icaro.tucanoar.com/video"
    if PROD else
    "ws://localhost:8000/video"
)
