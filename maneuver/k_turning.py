import time
from picarx import Picarx
import os
import sys
fpath = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(fpath)


def k_turning(px, dir):
    # theta_1 = atan((2*wheelbase*abs(par_dis_1))/(forward_dis^2 + par_dis_1^2))
    # theta_2 = atan((4*forward_dis*par_dis_1*wheelbase)/(par_dis_2*(forward_dis^2 + par_dis_1^2)))
    # t_1 = ((pi - 2*atan(forward_dis/par_dis_1))*(forward_dis^2 + par_dis_1^2))/(2*v*abs(par_dis_1))
    # t_2 = (par_dis_2*(forward_dis^2 + par_dis_1^2)*(4*atan(forward_dis/par_dis_1) - 2*pi + 180))/(4*forward_dis*par_dis_1*v)

    t_forward = 1
    t_turn = 0.25
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
    k_turning(px)
