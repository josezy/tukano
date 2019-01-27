import os

SRC_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = "%s/data" % BASE_DIR
LOGS_DIR = "%s/logs" % BASE_DIR


MAVLINK_ADDRESS = "udp:127.0.0.1:14551"
