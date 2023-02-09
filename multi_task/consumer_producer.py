import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from bus import Bus
import time
from line_tracking import Interpreter


def consumer_producer(wait_time, interpreter: Interpreter, bus_in: Bus, bus_out: Bus, bus_kill: Bus):
    while 1:
        # Read the kill signal to see if going to stop
        kill = bus_kill.read()
        if kill:
            break

        # Read data, process, and send out
        data = bus_in.read()
        bus_out.write(interpreter.process(data))

        # Sleep
        time.sleep(wait_time)
