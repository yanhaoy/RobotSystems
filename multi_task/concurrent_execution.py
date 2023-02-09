import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import concurrent.futures
from bus import Bus
from line_tracking import Controller, Sensor, Interpreter
from producer import producer
from consumer_producer import consumer_producer
from consumer import consumer
import time

bus_sensor = Bus()
bus_interpreter = Bus()
bus_kill = Bus()
controller = Controller()
sensor = Sensor()
interpreter = Interpreter()

input('Ready?')

bus_kill.write(False)
with concurrent.futures.ThreadPoolExecutor() as executor:
    eSensor = executor.submit(producer, 1e-2, sensor, bus_sensor, bus_kill)
    eInterpreter = executor.submit(consumer_producer, 1e-2, interpreter,
                                   bus_sensor, bus_interpreter, bus_kill)
    eController = executor.submit(consumer, 1e-2, controller, bus_interpreter, bus_kill)

    time.sleep(3)
    bus_kill.write(True)
