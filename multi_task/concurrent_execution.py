import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import concurrent.futures
from busses import Busses
from line_tracking import Controller, Sensor, Interpreter
from producers import producers
from consumer_producers import consumer_producers
from consumers import consumers
import time

busses_sensor = Busses()
busses_interpreter = Busses()
busses_kill = Busses()
controller = Controller()
sensor = Sensor()
interpreter = Interpreter()

input('Ready?')

busses_kill.write(False)
with concurrent.futures.ThreadPoolExecutor() as executor:
    eSensor = executor.submit(producers, 1e-2, sensor, busses_sensor, busses_kill)
    eInterpreter = executor.submit(consumer_producers, 1e-2, interpreter,
                                   busses_sensor, busses_interpreter, busses_kill)
    eController = executor.submit(consumers, 1e-2, controller, busses_interpreter, busses_kill)

    time.sleep(3)
    busses_kill.write(True)
