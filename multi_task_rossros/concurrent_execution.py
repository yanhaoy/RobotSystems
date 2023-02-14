import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import logging
from line_tracking import Controller, Sensor, Interpreter
from rossros import Bus, Consumer, ConsumerProducer, Producer, Timer, runConcurrently

logging.getLogger().setLevel(logging.INFO)

# Init all busses
bus_sensor = Bus(None, 'sensor_bus')
bus_interpreter = Bus(None, 'interpreter_bus')
bus_kill = Bus(False, 'kill_bus')

# Init all classes
controller = Controller()
sensor = Sensor()
interpreter = Interpreter()

# Get ready
input('Ready?')

# Wrap the sensor read into a producer
eSensor = Producer(
    sensor.read,  # function that will generate data
    bus_sensor,  # output data bus
    1e-2,  # delay between data generation cycles
    bus_kill,  # bus to watch for termination signal
    "Read greyscale sensor")

# Wrap the interpreter process into a consumer-producer
eInterpreter = ConsumerProducer(
    interpreter.process,  # function that will process data
    bus_sensor,  # input data buses
    bus_interpreter,  # output data bus
    1e-2,  # delay between data control cycles
    bus_kill,  # bus to watch for termination signal
    "Interprate signal")

# Wrap the controller drive into a consumer
eController = Consumer(
    controller.drive,  # function that will process data
    bus_interpreter,  # input data buses
    1e-2,  # delay between data control cycles
    bus_kill,  # bus to watch for termination signal
    "Control the cart")

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
eTimer = Timer(
    bus_kill,  # Output data bus
    3,  # Duration
    1e-2,  # Delay between checking for termination time
    bus_kill,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [eSensor, eInterpreter, eController, eTimer]

# Execute the list of producer-consumers concurrently
runConcurrently(producer_consumer_list)
