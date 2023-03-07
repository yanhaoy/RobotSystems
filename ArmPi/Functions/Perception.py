#!/usr/bin/env python3
import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

import cv2
import time
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
from CameraCalibration.CalibrationConfig import *


class Perception:
    def __init__(self) -> None:
        self.my_camera = Camera.Camera()
        self.my_camera.camera_open()
        self.size = (640, 480)
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        self.start_count_t1 = True
        self.t1 = 0
        self.start_pick_up = False
        self.world_X = 0
        self.world_Y = 0
        self.rotation_angle = 0
        self.last_x = 0
        self.last_y = 0
        self.track = False

    def sense(self, __target_color) -> None:

        # global roi
        # global rect
        # global count
        # global track
        # global get_roi
        # global center_list
        # global __isRunning
        # global unreachable
        # global detect_color
        # global action_finish
        # global rotation_angle
        # global last_x, last_y
        # global world_X, world_Y
        # global world_x, world_y
        # global start_count_t1, t1
        # global start_pick_up, first_move

        img = self.my_camera.frame
        if img is not None:
            img_copy = img.copy()
            img_h, img_w = img.shape[:2]
            cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
            cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

            frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
            frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
            # If it is detected with a area recognized object, the area will be detected until there is no object
            if get_roi and start_pick_up:
                get_roi = False
                frame_gb = getMaskROI(frame_gb, roi, self.size)

            frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # convert the image to LAB space

            area_max = 0
            areaMaxContour = 0
            if not start_pick_up:
                for i in color_range:
                    if i in __target_color:
                        detect_color = i
                        # mathematical operation on the original image and mask
                        frame_mask = cv2.inRange(
                            frame_lab, color_range[detect_color][0], color_range[detect_color][1])
                        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones(
                            (6, 6), np.uint8))  # Opening (morphology)
                        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones(
                            (6, 6), np.uint8))  # Closing (morphology)
                        contours = cv2.findContours(
                            closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find countour
                        areaMaxContour, area_max = getAreaMaxContour(
                            contours)  # find the maximum countour
                if area_max > 2500:  # find the maximum area
                    rect = cv2.minAreaRect(areaMaxContour)
                    box = np.int0(cv2.boxPoints(rect))

                    roi = getROI(box)  # get roi zone
                    get_roi = True

                    # get the center coordinates of block
                    img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)
                    world_x, world_y = convertCoordinate(
                        img_centerx, img_centery, self.size)  # convert to world coordinates

                    cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
                    cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1)  # draw center position
                    # compare the last coordinate to determine whether to move
                    distance = math.sqrt(pow(world_x - self.last_x, 2) +
                                         pow(world_y - self.last_y, 2))
                    self.last_x, self.last_y = world_x, world_y
                    self.track = True

                    # cumulative judgment
                    # if action_finish:
                    if distance < 0.3:
                        center_list.append((world_x, world_y))
                        # count += 1
                        if self.start_count_t1:
                            self.start_count_t1 = False
                            self.t1 = time.time()
                        if time.time() - self.t1 > 1.5:
                            self.rotation_angle = rect[2]
                            self.start_count_t1 = True
                            self.world_X, self.world_Y = np.mean(
                                np.array(center_list).reshape(-1, 2), axis=0)
                            # count = 0
                            center_list = []
                            start_pick_up = True
                    else:
                        # self.t1 = time.time()
                        self.start_count_t1 = True
                        # count = 0
                        center_list = []

        return img, self.track, start_pick_up, (self.world_X, self.world_Y, self.rotation_angle)

# find the maximum area contour
# the parameter is a list of contours to be compared


def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # traversal all the contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # calculate the countour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # only when the area is greater than 300, the contour of the maximum area is effective to filter interference
                area_max_contour = c

    return area_max_contour, contour_area_max  # return the maximum area countour
