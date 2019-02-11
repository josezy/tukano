import os


MAVLINK_ADDRESS = "tcp:192.168.1.53:5760"


################################################################################
#### Directory contants
################################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = "{}/data".format(BASE_DIR)
LOGS_DIR = "{}/logs".format(BASE_DIR)


################################################################################
#### External hardware pins
################################################################################

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

ALT_THRESHOLD = 10              # Collect data above N meters
DATA_COLLECT_TIMESPAN = 0.2     # Collect data every Z seconds


################################################################################
#### Redis config
################################################################################
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0

REDIS_CONF = {'host': REDIS_HOST, 'port': REDIS_PORT, 'db': REDIS_DB}

CELERY_BROKER = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)
