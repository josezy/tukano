import os


MAVLINK_ADDRESS = "udp:127.0.0.1:14551"


################################################################################
#### Directory contants
################################################################################

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = "%s/data" % BASE_DIR
LOGS_DIR = "%s/logs" % BASE_DIR


################################################################################
#### External hardware pins
################################################################################

# AM2302 Temperature, Humidity sensor
AM2302_PINS = {
    'out': 4,
}

# BMP183 Temperature, Pressure sensor (SPI Interface)
BMP183_PINS = {
    'sck': 11,
    'mosi': 10,
    'miso': 9,
    'cs': 22,
}
