#!/usr/bin/env python3
from numpy import sign


class Interpreter(object):
    def __init__(self, sensitivity=50, polarity=False, sensor_type='grayscale', distance_threshold=25):
        # Setup parameters
        self.sensor_type = sensor_type
        if self.sensor_type is 'grayscale':
            # polarity: True for darker line
            self.sensitivity = sensitivity
            self.polarity = polarity
        elif self.sensor_type is 'ultrasonic':
            self.distance_threshold = distance_threshold

    def process_grayscale(self, fl_list):
        # Check message
        if fl_list is None:
            return None

        # Compute difference
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

    def process_ultrasonic(self, dis):
        # Stop the robot when something is close
        if dis is None or dis > 25 or dis < 0:
            return False
        else:
            return True

    def process(self, read):
        # Call the corresponding process function
        if self.sensor_type is 'grayscale':
            return self.process_grayscale(read)
        elif self.sensor_type is 'ultrasonic':
            return self.process_ultrasonic(read)
