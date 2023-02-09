import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from line_tracking import Controller, Sensor, Interpreter
from rossros import Bus, Consumer, ConsumerProducer, Producer, Timer, runConcurrently

# Init all busses
busses_grayscale_sensor = Bus(None, 'grayscale_sensor_bus')
busses_ultrasonic_sensor = Bus(None, 'ultrasonic_sensor_bus')
busses_grayscale_interpreter = Bus(None, 'grayscale_interpreter_bus')
busses_ultrasonic_interpreter = Bus(False, 'ultrasonic_interpreter_bus')
busses_timer = Bus(False, 'timer_bus')

# Init all classes
controller = Controller()
grayscale_sensor = Sensor(sensor_type='grayscale')
ultrasonic_sensor = Sensor(sensor_type='ultrasonic')
grayscale_interpreter = Interpreter(sensor_type='grayscale')
ultrasonic_interpreter = Interpreter(sensor_type='ultrasonic')

# Get ready
input('Ready?')

# Wrap the sensor read into a producer
eGrayscaleSensor = Producer(
    grayscale_sensor.read,  # function that will generate data
    busses_grayscale_sensor,  # output data bus
    1e-2,  # delay between data generation cycles
    (busses_timer, busses_ultrasonic_interpreter),  # bus to watch for termination signal
    "Read grayscale sensor")

# Wrap the sensor read into a producer
eUltrasonicSensor = Producer(
    ultrasonic_sensor.read,  # function that will generate data
    busses_ultrasonic_sensor,  # output data bus
    1e-2,  # delay between data generation cycles
    (busses_timer, busses_ultrasonic_interpreter),  # bus to watch for termination signal
    "Read ultrasonic sensor")

# Wrap the interpreter process into a consumer-producer
eGrayscaleInterpreter = ConsumerProducer(
    grayscale_interpreter.process,  # function that will process data
    busses_grayscale_sensor,  # input data buses
    busses_grayscale_interpreter,  # output data bus
    1e-2,  # delay between data control cycles
    (busses_timer, busses_ultrasonic_interpreter),  # bus to watch for termination signal
    "Interprate grayscale signal")

# Wrap the interpreter process into a consumer-producer
eUltrasonicInterpreter = ConsumerProducer(
    ultrasonic_interpreter.process,  # function that will process data
    busses_ultrasonic_sensor,  # input data buses
    busses_ultrasonic_interpreter,  # output data bus
    1e-2,  # delay between data control cycles
    (busses_timer, busses_ultrasonic_interpreter),  # bus to watch for termination signal
    "Interprate ultrasonic signal")

# Wrap the controller drive into a consumer
eController = Consumer(
    controller.drive,  # function that will process data
    busses_grayscale_interpreter,  # input data buses
    1e-2,  # delay between data control cycles
    (busses_timer, busses_ultrasonic_interpreter),  # bus to watch for termination signal
    "Control the cart")

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
eTimer = Timer(
    busses_timer,  # Output data bus
    3,  # Duration
    1e-2,  # Delay between checking for termination time
    busses_timer,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [eGrayscaleSensor, eUltrasonicSensor,
                          eGrayscaleInterpreter, eUltrasonicInterpreter, eController, eTimer]

# Execute the list of producer-consumers concurrently
runConcurrently(producer_consumer_list)
