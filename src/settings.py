import os
import ssl
import logging

from util.system import load_env_settings

os.environ['MAVLINK_DIALECT'] = "mav_tukano"

SLEEPING_TIME = 0.0001
PROD = os.getenv('TUKANO_ENV', 'DEV') == "PROD"  # Development flag
LOGGING_LEVEL = "INFO"

PLATE = "00000000"

###############################################################################
# Paths and files
###############################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = f"{BASE_DIR}/data"
PICS_DIR = f"{DATA_DIR}/pics"
VIDEOS_DIR = f"{DATA_DIR}/videos"
LOGS_DIR = f"{DATA_DIR}/logs"
ENV_DIR = f"{BASE_DIR}/env"

ENV_DEFAULTS_FILE = f"{ENV_DIR}/defaults.env"

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
RECORD_START_ALT = 9                    # Start recording video above N meters
RECORD_STOP_ALT = 1                     # Stop recording video below N meters

STREAM_VIDEO_JPEG_QUALITY = 50          # Stream video quality

###############################################################################
# Load variables from .env file and os.environ
###############################################################################

# settings set via env/defaults.env
ENV_DEFAULTS = load_env_settings(dotenv_path=ENV_DEFAULTS_FILE, defaults=globals())
globals().update(ENV_DEFAULTS)

# settings set via environment variables
ENV_OVERRIDES = load_env_settings(env=dict(os.environ), defaults=globals())
globals().update(ENV_OVERRIDES)

###############################################################################
# Logging settings
###############################################################################

LOGGING_KWARGS = {
    'level': getattr(logging, LOGGING_LEVEL),  # DEBUG-INFO-WARNING-ERROR-CRITICAL
    'format': '[%(levelname)s] %(asctime)s: %(message)s'
}

logging.basicConfig(**LOGGING_KWARGS)
logging.info(f"Working on {'production' if PROD else 'development'}")

###############################################################################
# Connection parameters
###############################################################################

MAVLINK_TUKANO = (
    {
        'device': "/dev/ttyACM0",
        'baud': 57600,
    }
    if PROD else
    {
        'device': "tcp:localhost:5760",
    }
)

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

WS_CONNECTION_PARAMS = {'sslopt': {"cert_reqs": ssl.CERT_NONE}} if PROD else {}

# WebSocket for mavlink
assert type(PLATE) == str and len(PLATE) == 8, "No PLATE set"
WS_MAV_ENDPOINT = (
    f"wss://ikaro.tucanorobotics.co/mavlink/plate/{PLATE}"
    if PROD else
    f"ws://localhost:3000/mavlink/plate/{PLATE}"
)

WS_MAV_MSG_TYPES = (
    'HEARTBEAT', 'TUKANO_DATA', 'GLOBAL_POSITION_INT', 'SYS_STATUS', 'VFR_HUD',
    'GPS_RAW_INT', 'COMMAND_ACK', 'ATTITUDE', 'STATUSTEXT', 'MISSION_COUNT',
    'MISSION_ITEM', 'PARAM_VALUE', 'HOME_POSITION'
)
