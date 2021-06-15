import logging

from tango.server import run

from .TEMSpyDevice import TEMSpyDevice


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("starting TEMSpyDevice")
    run((TEMSpyDevice,))
    logger.debug("stopping TEMSpyDevice")
