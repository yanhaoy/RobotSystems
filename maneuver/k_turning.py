import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
from picarx import Picarx


def k_turning(px, dir):
    """
    Perform the k-turning along the specified direction.

    :param px: The car hardware interface.
    :param dir: Turning direction, can be 'left' or 'right'.
    """
    # Define turning parameters
    t_forward = 0.6
    t_turn = 1.2
    vel = 50
    if dir == 'left':
        ang = -30
    else:
        ang = 30

    # Forwad turning
    px.turn(ang)
    px.run(vel)
    time.sleep(t_forward)
    px.run(0)

    # Backward turning
    px.turn(-ang)
    px.run(-vel)
    time.sleep(t_turn)
    px.run(0)

    # Forward turning
    px.turn(ang)
    px.run(vel)
    time.sleep(t_forward)
    px.run(0)

    # Stop
    px.stop()
    time.sleep(.2)


if __name__ == "__main__":
    px = Picarx()
    k_turning(px, 'left')
