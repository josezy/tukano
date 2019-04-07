import os

os.environ['MAVLINK_DIALECT'] = "mav_tukano"

SLEEPING_TIME = 0.000001
VERBOSE = False

################################################################################
#### Directory contants
################################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = "{}/data".format(BASE_DIR)
PICS_DIR = "{}/pics".format(DATA_DIR)
FACES_DIR = "{}/faces".format(DATA_DIR)

################################################################################
#### Connection parameters
################################################################################

## Aircraft connections
MAVLINK_VEHICLE = {
    # 'device': "tcp:localhost:5760", # SITL on local PC
    # 'device': "tcp:192.168.1.53:5760", # SITL on remote PC
    # 'device': "/dev/ttyAMA0", # UART on ARM architectures
    'device': "/dev/ttyS0", # UART on x86 and x86_64 architectures
    'baud': 57600,
}
MAVLINK_TUKANO = {
    'device': "udp:127.0.0.1:14551",
}
MAVLINK_GROUND = {
    'device': "/dev/ttyUSB0",
    # 'device': "udp:127.0.0.1:14552",
    'baud': 115200,
}

## Ground connections
MAVLINK_AIRCRAFT = {
    'device': "/dev/ttyUSB0",
    # 'device': "udp:127.0.0.1:14552",
    'baud': 115200,
}
MAVLINK_GCS = {
    'device': "udp:127.0.0.1:14550",
}


################################################################################
#### External hardware pins
################################################################################

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

################################################################################
#### Flight tasks parameters
################################################################################

ALT_THRESHOLD = 10000                   # Collect data above N milimeters
DATA_COLLECT_TIMESPAN = 0.4             # Collect data every Z seconds
MAX_SAMPLES_PER_MAVLINK_MESSAGE = 1     # Amount of samples to send over 1 mav msg
MAVLINK_SAMPLES_TIMESPAN = 0.4          # Time between custom mavlink messages

################################################################################
#### Redis config
################################################################################
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 2

REDIS_CONF = {'host': REDIS_HOST, 'port': REDIS_PORT, 'db': REDIS_DB}

CELERY_BROKER = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)
