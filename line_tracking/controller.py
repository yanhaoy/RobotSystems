import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from picarx import Picarx


class Controller(object):
    def __init__(self, steering_angle=5, vel=50):
        # self.sensor = Sensor()
        # self.interpreter = Interpreter()
        self.steering_angle = steering_angle
        self.vel = 50
        self.px = Picarx()

    def drive(self, dir):
        self.px.turn(dir*self.steering_angle)
        self.px.run(self.vel)
