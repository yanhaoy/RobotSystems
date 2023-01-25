import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
from picarx import Picarx


def move(px):
    """
    Perform a test move.

    :param px: The car hardware interface.
    """
    # Do a forward turning
    px.turn(-30)
    px.run(50)
    time.sleep(1)

    # Stop
    px.stop()
    time.sleep(.2)


if __name__ == "__main__":
    px = Picarx()
    move(px)
