import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from bus import Bus
import time
from line_tracking import Sensor


def producer(wait_time, sensor: Sensor, bus: Bus, bus_kill: Bus):
    while 1:
        # Read the kill signal to see if going to stop
        kill = bus_kill.read()
        if kill:
            break

        # Send out sensor reading
        bus.write(sensor.read())

        # Sleep
        time.sleep(wait_time)
