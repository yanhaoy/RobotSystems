import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from picarx import Picarx


class Controller(object):
    def __init__(self, steering_angle_scale=5, vel=50):
        # Setup parameters
        self.steering_angle_scale = steering_angle_scale
        self.steering_angle = 0
        self.vel = vel

        # Init driver
        self.px = Picarx()
        self.px.run(0)
        self.px.turn(0)

    def drive(self, dir):
        # Stop if no info
        if dir is None:
            self.px.run(0)
            return

        # Scale steering angle
        steering_angle_current = -dir*self.steering_angle_scale

        # Low pass filter
        self.steering_angle = 0.75*self.steering_angle+0.25*steering_angle_current

        # Drive
        self.px.turn(round(self.steering_angle))
        self.px.run(self.vel)
