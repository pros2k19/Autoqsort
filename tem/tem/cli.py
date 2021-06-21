import logging

from tango.server import run

from .QSortTEMDevice import QSortTEMDevice


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("starting QSortTEMDevice")
    run((QSortTEMDevice,))
    logger.debug("stopping QSortTEMDevice")
