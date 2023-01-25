import time
from sensor import Sensor
from controller import Controller
from interpreter import Interpreter


def line_tracking():
    controller = Controller()
    sensor = Sensor()
    interpreter = Interpreter()
    input()
    while 1:
        val = sensor.read()
        dir = interpreter.process(val)
        controller.drive(dir)
        time.sleep(0.001)


if __name__ == "__main__":
    line_tracking()
