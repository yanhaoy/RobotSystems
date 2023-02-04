import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from busses import Busses
import time
from line_tracking import Sensor


def producers(wait_time, sensor: Sensor, busses: Busses, busses_kill: Busses):
    while 1:
        kill = busses_kill.read()
        if kill:
            break
        busses.write(sensor.read())
        time.sleep(wait_time)
