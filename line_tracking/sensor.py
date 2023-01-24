#!/usr/bin/env python3
import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

try:
    from robot_hat import ADC
except ImportError:
    print("This computer does not appear to be a PiCar-X system (robot_hat is not present). Shadowing hardware calls with substitute functions")
    from sim_robot_hat import ADC


class Sensor(object):
    def __init__(self, pin0='A0', pin1='A1', pin2='A2'):
        self.chn_0 = ADC(pin0)
        self.chn_1 = ADC(pin1)
        self.chn_2 = ADC(pin2)
        self.zero_value = [None]*3

        self.zero()

    def read(self, zero=True):
        # The brighter the area, the larger the value obtained
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())

        if zero:
            for i in range(3):
                adc_value_list[i] -= self.zero_value[i]

        return adc_value_list

    def zero(self):
        self.zero_value = self.read(zero=False)
