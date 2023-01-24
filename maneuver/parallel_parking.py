import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
from picarx import Picarx


def parallel_parking(px, dir):
    # t_turn = (wheelbase*acos((2*wheelbase - par_dis*tan(theta))/(2*wheelbase)))/(v*tan(theta))
    # t_forward = (wheelbase*(1 - (2*wheelbase - par_dis*tan(theta))^2/(4*wheelbase^2))^(1/2))/(v*tan(theta))

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
