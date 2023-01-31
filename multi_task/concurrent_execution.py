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

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    eSensor = executor.submit(producers, busses_sensor, 1e3)
    eInterpreter = executor.submit(consumer_producers, busses_sensor, busses_interpreter, 1e3)
    eController = executor.submit(consumers, busses_interpreter, 1e3)

eSensor.result()
eInterpreter.result()
eController.result()
