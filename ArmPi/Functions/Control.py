#!/usr/bin/env python3
import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import time
import atexit
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *


class Control:
    def __init__(self, share) -> None:
        initMove(share)
        atexit.register(initMove, share)

    def move(self, share):
        # different colors blocks place coordinates(x, y, z)
        coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }

        if share.first_move and share.start_pick_up:  # when an object be detected for the first time
            share.action_finish = False
            set_rgb(share.detect_color)
            setBuzzer(0.1)
            # do not fill running time parameters,self-adaptive running time
            result = share.AK.setPitchRangeMoving(
                (share.world_X, share.world_Y - 2, 5), -90, -90, 0)
            if result == False:
                share.unreachable = True
            else:
                share.unreachable = False
            time.sleep(result[2]/1000)  # the thrid item of return parameter is time
            share.start_pick_up = False
            share.first_move = False
            share.action_finish = True
        elif not share.first_move and not share.unreachable:  # not the first time to detected object
            set_rgb(share.detect_color)
            if share.track:  # if it is following state
                share.AK.setPitchRangeMoving((share.world_x, share.world_y - 2, 5), -90, -90, 0, 20)
                time.sleep(0.02)
                share.track = False
            if share.start_pick_up:  # if it is detected that the block has not removed for a period of time, start to pick up
                share.action_finish = False

                Board.setBusServoPulse(1, share.servo1 - 280, 500)  # claw open
                # calculate angle at that the clamper gripper needs to rotate
                servo2_angle = getAngle(share.world_X, share.world_Y, share.rotation_angle)
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.8)

                share.AK.setPitchRangeMoving((share.world_X, share.world_Y, 2), -
                                             90, -90, 0, 1000)  # reduce height
                time.sleep(2)

                Board.setBusServoPulse(1, share.servo1, 500)  # claw colsed
                time.sleep(1)

                Board.setBusServoPulse(2, 500, 500)
                share.AK.setPitchRangeMoving((share.world_X, share.world_Y, 12), -
                                             90, -90, 0, 1000)  # Armpi robot arm up
                time.sleep(1)

                # Sort and place different colored blocks
                result = share.AK.setPitchRangeMoving(
                    (coordinate[share.detect_color][0], coordinate[share.detect_color][1], 12), -90, -90, 0)
                time.sleep(result[2]/1000)

                servo2_angle = getAngle(
                    coordinate[share.detect_color][0], coordinate[share.detect_color][1], -90)
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.5)

                share.AK.setPitchRangeMoving((coordinate[share.detect_color][0], coordinate[share.detect_color]
                                              [1], coordinate[share.detect_color][2] + 3), -90, -90, 0, 500)
                time.sleep(0.5)

                share.AK.setPitchRangeMoving((coordinate[share.detect_color]), -90, -90, 0, 1000)
                time.sleep(0.8)

                Board.setBusServoPulse(1, share.servo1 - 200, 500)  # gripper open，put down object
                time.sleep(0.8)

                share.AK.setPitchRangeMoving(
                    (coordinate[share.detect_color][0], coordinate[share.detect_color][1], 12), -90, -90, 0, 800)
                time.sleep(0.8)

                initMove(share)  # back to initial position
                time.sleep(1.5)

                share.detect_color = 'None'
                share.first_move = True
                share.get_roi = False
                share.action_finish = True
                share.start_pick_up = False
                set_rgb(share.detect_color)
            else:
                time.sleep(0.01)

        return share


def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()


def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)


def initMove(share):
    Board.setBusServoPulse(1, share.servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    share.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
