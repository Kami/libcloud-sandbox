import sys
import os.path
import logging

from libcloud_sandbox.settings import LOG_FORMAT

def get_and_setup_logger():
    logger = logging.getLogger('libcloud_sandbox.json-rpc.server')
    logger.setLevel(logging.INFO)
    handler=logging.StreamHandler(sys.__stdout__)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
