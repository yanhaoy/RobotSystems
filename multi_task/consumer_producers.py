import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from busses import Busses
import time
from line_tracking import Interpreter


def consumer_producers(wait_time, interpreter: Interpreter, busses_in: Busses, busses_out: Busses, busses_kill: Busses):
    while 1:
        # Read the kill signal to see if going to stop
        kill = busses_kill.read()
        if kill:
            break

        # Read data, process, and send out
        data = busses_in.read()
        busses_out.write(interpreter.process(data))

        # Sleep
        time.sleep(wait_time)
