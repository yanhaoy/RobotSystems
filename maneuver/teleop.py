import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
from picarx import Picarx
from parallel_parking import parallel_parking
from k_turning import k_turning


def teleop(px):
    """
    Teleoperation interface.

    :param px: The car hardware interface.
    """
    vel = 50
    dang = 5
    ang = 0
    dt = 0.25

    while 1:
        print('Operation list: \n\
w, a, s, and d for forward, backward, and steering \n\
h and j for parrell parking left and right \n\
k and l for k-turning left and right \n\
q for quit \n\
Enter your operation:')
        x = input()

        if x == 'w':
            px.run(vel)
            time.sleep(dt)
            px.run(0)
        elif x == 's':
            px.run(-vel)
            time.sleep(dt)
            px.run(0)
        elif x == 'a':
            ang -= dang
            px.turn(ang)
        elif x == 'd':
            ang += dang
            px.turn(ang)
        elif x == 'k':
            k_turning(px, 'left')
        elif x == 'l':
            k_turning(px, 'right')
        elif x == 'h':
            parallel_parking(px, 'left')
        elif x == 'j':
            parallel_parking(px, 'right')
        elif x == 'q':
            break
        else:
            print('Unknown operation')
            continue

    px.stop()
    time.sleep(.2)


if __name__ == "__main__":
    px = Picarx()
    teleop(px)
