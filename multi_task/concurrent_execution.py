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

busses_sensor = Busses()
busses_interpreter = Busses()
controller = Controller()
sensor = Sensor()
interpreter = Interpreter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    eSensor = executor.submit(producers, 1e-2, sensor, busses_sensor)
    eInterpreter = executor.submit(consumer_producers, 1e-2, interpreter,
                                   busses_sensor, busses_interpreter)
    eController = executor.submit(consumers, 1e-1, controller, busses_interpreter)

eSensor.result()
eInterpreter.result()
eController.result()
