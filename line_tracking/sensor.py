#!/usr/bin/env python3
import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
try:
    from robot_hat import ADC, Pin
    from robot_hat.utils import reset_mcu

    reset_mcu()
    time.sleep(0.2)
except ImportError:
    print("This computer does not appear to be a PiCar-X system (robot_hat is not present). Shadowing hardware calls with substitute functions")
    from sim_robot_hat import ADC, Pin


class Sensor(object):
    def __init__(self,
                 grayscale_pins: list = ['A0', 'A1', 'A2'],
                 ultrasonic_pins: list = ['D2', 'D3'],
                 sensor_type: str = 'grayscale',
                 timeout=0.02):
        # Setup parameters
        self.sensor_type = sensor_type
        if self.sensor_type is 'grayscale':
            self.chn_0 = ADC(grayscale_pins[0])
            self.chn_1 = ADC(grayscale_pins[1])
            self.chn_2 = ADC(grayscale_pins[2])
        elif self.sensor_type is 'ultrasonic':
            self.trig = Pin(ultrasonic_pins[0])
            self.echo = Pin(ultrasonic_pins[1])
            self.timeout = timeout

    def read_grayscale(self):
        # The brighter the area, the larger the value obtained
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())

        return adc_value_list

    def read_ultrasonic(self):
        # It was copied from robot_hat, looks like a TOF
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while self.echo.value() == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value() == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        return cm

    def read(self):
        # Call the corresponding function
        if self.sensor_type is 'grayscale':
            return self.read_grayscale()
        elif self.sensor_type is 'ultrasonic':
            # It was copied from robot_hat
            for i in range(10):
                a = self.read_ultrasonic()
                if a != -1:
                    return a
            return None


if __name__ == "__main__":
    sensor = Sensor()
    while 1:
        print(sensor.read())
        time.sleep(0.1)
