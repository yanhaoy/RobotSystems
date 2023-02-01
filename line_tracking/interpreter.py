#!/usr/bin/env python3
from numpy import sign


class Interpreter(object):
    def __init__(self, sensitivity=50, polarity=False):
        # polarity: True for darker line
        self.sensitivity = sensitivity
        self.polarity = polarity

    def process(self, fl_list):
        diff = fl_list[0] - fl_list[2]
        # Only turn when beyond the sensitivity
        if abs(diff) < self.sensitivity:
            return 0
        else:
            dir = sign(diff)
            if self.polarity:
                return -dir
            else:
                return dir
