import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import logging
from Control import Control
from Perception import Perception
from ShareData import ShareData
from rossros import Bus, ConsumerProducer, Timer, runConcurrently

logging.getLogger().setLevel(logging.INFO)

# Init all busses
share = ShareData()
bus_share = Bus(share, 'bus_share')
bus_kill = Bus(False, 'bus_kill')

# Init all classes
controller = Control(share)
sensor = Perception()

# Get ready
input('Ready?')

# Wrap the interpreter process into a consumer-producer
eController = ConsumerProducer(
    controller.move,  # function that will process data
    bus_share,  # input data buses
    bus_share,  # output data bus
    1e-1,  # delay between data control cycles
    bus_kill,  # bus to watch for termination signal
    "Controller")

# Wrap the interpreter process into a consumer-producer
eSensor = ConsumerProducer(
    sensor.sense,  # function that will process data
    bus_share,  # input data buses
    bus_share,  # output data bus
    1e-1,  # delay between data control cycles
    bus_kill,  # bus to watch for termination signal
    "Sensor")

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
eTimer = Timer(
    bus_kill,  # Output data bus
    60,  # Duration
    1e-1,  # Delay between checking for termination time
    bus_kill,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [eSensor, eController, eTimer]

# Execute the list of producer-consumers concurrently
runConcurrently(producer_consumer_list)
