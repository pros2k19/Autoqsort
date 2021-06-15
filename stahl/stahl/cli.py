import logging

from tango.server import run

from .QSortStahlDevice import QSortStahlDevice


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("starting QSortStahlDevice")
    run((QSortStahlDevice,))
    logger.debug("stopping QSortStahlDevice")
