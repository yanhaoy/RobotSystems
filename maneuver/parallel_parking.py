import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
from picarx import Picarx


def parallel_parking(px, dir):
    """
    Perform the parallel parking along the specified direction.

    :param px: The car hardware interface.
    :param dir: Parking direction, can be 'left' or 'right'.
    """
    # Define parking parameters
    t_forward = 0.4
    t_turn = 0.5
    vel = 50
    if dir == 'left':
        ang = -30
    else:
        ang = 30

    # Forwad
    px.turn(0)
    px.run(vel)
    time.sleep(t_forward)
    px.run(0)

    # Backward turning 1
    px.turn(ang)
    px.run(-vel)
    time.sleep(t_turn)
    px.run(0)

    # Backward turning 2
    px.turn(-ang)
    px.run(-vel)
    time.sleep(t_turn)
    px.run(0)

    # Forward
    px.turn(0)
    px.run(vel)
    time.sleep(t_forward)
    px.run(0)

    # Stop
    px.stop()
    time.sleep(.2)


if __name__ == "__main__":
    px = Picarx()
    parallel_parking(px)
