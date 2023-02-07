import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import concurrent.futures
from line_tracking import Controller, Sensor, Interpreter
from rossros import Bus, Consumer, ConsumerProducer, Producer, Printer, Timer, runConcurrently
import time

busses_sensor = Bus(None, 'sensor_bus')
busses_interpreter = Bus(None, 'nterpreter_bus')
busses_kill = Bus(0, 'kill_bus')
controller = Controller()
sensor = Sensor()
interpreter = Interpreter()

input('Ready?')

# Wrap the square wave signal generator into a producer
eSensor = Producer(
    sensor.read,  # function that will generate data
    busses_sensor,  # output data bus
    1e-2,  # delay between data generation cycles
    busses_kill,  # bus to watch for termination signal
    "Read greyscale sensor")

# Wrap the multiplier function into a consumer-producer
eInterpreter = ConsumerProducer(
    interpreter.process,  # function that will process data
    busses_sensor,  # input data buses
    busses_interpreter,  # output data bus
    1e-2,  # delay between data control cycles
    busses_kill,  # bus to watch for termination signal
    "Interprate signal")

# Wrap the multiplier function into a consumer
eController = Consumer(
    controller.drive,  # function that will process data
    busses_interpreter,  # input data buses
    1e-2,  # delay between data control cycles
    busses_kill,  # bus to watch for termination signal
    "Control the cart")

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
eTimer = Timer(
    busses_kill,  # Output data bus
    3,  # Duration
    1e-2,  # Delay between checking for termination time
    busses_kill,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [eSensor, eInterpreter, eController, eTimer]

# Execute the list of producer-consumers concurrently
runConcurrently(producer_consumer_list)
