import os  # nopep8
import sys  # nopep8
fpath = os.path.dirname(__file__)  # nopep8
sys.path.append(fpath)  # nopep8

import time
import os
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
import atexit
from numpy import deg2rad, sign
from math import *
try:
    from robot_hat import Pin, PWM, Servo, fileDB
    from robot_hat import Grayscale_Module, Ultrasonic
    from robot_hat.utils import reset_mcu

    reset_mcu()
    time.sleep(0.2)
except ImportError:
    print("This computer does not appear to be a PiCar-X system (robot_hat is not present). Shadowing hardware calls with substitute functions")
    from sim_robot_hat import Pin, PWM, Servo, fileDB
    from sim_robot_hat import Grayscale_Module, Ultrasonic

# Set up logger
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

# user and User home directory
User = os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()
UserHome = os.popen('getent passwd %s | cut -d: -f 6' % User).readline().strip()
# print(User)  # pi
# print(UserHome) # /home/pi
config_file = '%s/.config/picar-x/picar-x.conf' % UserHome


class Picarx(object):
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02

    # servo_pins: direction_servo, camera_servo_1, camera_servo_2
    # motor_pins: left_swicth, right_swicth, left_pwm, right_pwm
    # grayscale_pins: 3 adc channels
    # ultrasonic_pins: tring, echo
    # config: path of config file
    def __init__(self,
                 servo_pins: list = ['P0', 'P1', 'P2'],
                 motor_pins: list = ['D4', 'D5', 'P12', 'P13'],
                 grayscale_pins: list = ['A0', 'A1', 'A2'],
                 ultrasonic_pins: list = ['D2', 'D3'],
                 config: str = config_file,
                 ):

        # config_flie
        self.config_flie = fileDB(config, 774, User)
        # servos init
        self.camera_servo_pin1 = Servo(PWM(servo_pins[0]))
        self.camera_servo_pin2 = Servo(PWM(servo_pins[1]))
        self.dir_servo_pin = Servo(PWM(servo_pins[2]))
        self.dir_cal_value = int(self.config_flie.get("picarx_dir_servo", default_value=0))
        self.cam_cal_value_1 = int(self.config_flie.get("picarx_cam_servo1", default_value=0))
        self.cam_cal_value_2 = int(self.config_flie.get("picarx_cam_servo2", default_value=0))
        self.dir_servo_pin.angle(self.dir_cal_value)
        self.camera_servo_pin1.angle(self.cam_cal_value_1)
        self.camera_servo_pin2.angle(self.cam_cal_value_2)
        # motors init
        self.left_rear_dir_pin = Pin(motor_pins[0])
        self.right_rear_dir_pin = Pin(motor_pins[1])
        self.left_rear_pwm_pin = PWM(motor_pins[2])
        self.right_rear_pwm_pin = PWM(motor_pins[3])
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = self.config_flie.get("picarx_dir_motor", default_value="[1,1]")
        self.cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip("[]").split(",")]
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        # Register the exit function that sets the motor speed and steering angle to zero
        atexit.register(self.stop)

        # Approximate dimensions for steering differential drive
        self.wheelbase = 11.
        self.trackwidth = 11.

    def set_motor_speed(self, motor, speed):
        # global cali_speed_value,cali_dir_value
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        # Use actual velocity instead of scaled
        # if speed != 0:
        #     speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self, value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self, motor, value):
        # 1: positive direction
        # -1:negative direction
        motor -= 1
        # if value == 1:
        #     self.cali_dir_value[motor] = -1 * self.cali_dir_value[motor]
        # self.config_flie.set("picarx_dir_motor", self.cali_dir_value)
        if value == 1:
            self.cali_dir_value[motor] = 1
        elif value == -1:
            self.cali_dir_value[motor] = -1
        self.config_flie.set("picarx_dir_motor", self.cali_dir_value)

    def dir_servo_angle_calibration(self, value):
        self.dir_cal_value = value
        self.config_flie.set("picarx_dir_servo", "%s" % value)
        self.dir_servo_pin.angle(value)

    def set_dir_servo_angle(self, value):
        self.dir_current_angle = value
        angle_value = value + self.dir_cal_value
        self.dir_servo_pin.angle(angle_value)

    def camera_servo1_angle_calibration(self, value):
        self.cam_cal_value_1 = value
        self.config_flie.set("picarx_cam_servo1", "%s" % value)
        self.camera_servo_pin1.angle(value)

    def camera_servo2_angle_calibration(self, value):
        self.cam_cal_value_2 = value
        self.config_flie.set("picarx_cam_servo2", "%s" % value)
        self.camera_servo_pin2.angle(value)

    def set_camera_servo1_angle(self, value):
        self.camera_servo_pin1.angle(-1*(value + -1*self.cam_cal_value_1))

    def set_camera_servo2_angle(self, value):
        self.camera_servo_pin2.angle(-1*(value + -1*self.cam_cal_value_2))

    def set_power(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed)

    def backward(self, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0
            # print("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed * power_scale)
            else:
                self.set_motor_speed(1, -1*speed * power_scale)
                self.set_motor_speed(2, speed)
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)

    def forward(self, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0
            # print("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, 1*speed * power_scale)
                self.set_motor_speed(2, -speed)
                # print("current_speed: %s %s"%(1*speed * power_scale, -speed))
            else:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -1*speed * power_scale)
                # print("current_speed: %s %s"%(speed, -1*speed * power_scale))
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)

    def run(self, speed):
        """
        Run the robot at the given speed.

        :param speed: The running speed, can be negative, 0, or positive.
        """
        # Get variables
        theta = self.dir_current_angle
        wheelbase = self.wheelbase
        trackwidth = self.trackwidth

        # Computes the speed difference between two wheels based on geometry. Assume the specified speed is achieved at the center between the two wheels.
        v_diff = round((trackwidth*speed*tan(deg2rad(theta)))/(2*wheelbase))

        # Set motor speed
        self.set_motor_speed(1, speed - v_diff)
        self.set_motor_speed(2, -(speed + v_diff))

    def turn(self, theta_desired):
        """
        Turn the robot steering angle smoothly.

        :param theta_desired: The desired steering angle in degrees, can be negative, 0, or positive.
        """
        theta_desired = min(max(theta_desired, -35), 35)
        self.set_dir_servo_angle(theta_desired)

    def stop(self):
        """
        Stop the robot by turning off the motors and steering to zero.
        """
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)
        self.turn(0)

    def get_distance(self):
        return self.ultrasonic.read()

    def set_grayscale_reference(self, value):
        self.get_grayscale_reference = value

    def get_grayscale_data(self):
        return list.copy(self.grayscale.get_grayscale_data())

    def get_line_status(self, gm_val_list):
        return str(self.grayscale.get_line_status(gm_val_list))


if __name__ == "__main__":
    px = Picarx()
    px.forward(50)
    time.sleep(1)
    px.stop()
