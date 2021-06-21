import logging

from tango.server import run

from .CorrectorDevice import CorrectorDevice


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("starting CorrectorDevice")
    run((CorrectorDevice,))
    logger.debug("stopping CorrectorDevice")
