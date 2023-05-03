import logging

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

CONFIG = {
    "max_transfer": 16,                 # in bytes
}

CLIENT_DISCONNECT_KEY = 'hfQf5we98FiVhauG'
