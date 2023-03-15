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

        return

    def sense(self, share) -> None:
        img = self.my_camera.frame
        if img is None:
            return share

        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        frame_resize = cv2.resize(img_copy, share.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        # If it is detected with a aera recognized object, the area will be detected ubtil there is no object
        if share.get_roi and share.start_pick_up:
            share.get_roi = False
            frame_gb = getMaskROI(frame_gb, share.roi, share.size)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # convert the image to LAB space

        area_max = 0
        areaMaxContour = 0
        if not share.start_pick_up:
            for i in color_range:
                if i in share.__target_color:
                    share.detect_color = i
                    # mathematical operation on the original image and mask
                    frame_mask = cv2.inRange(
                        frame_lab, color_range[share.detect_color][0], color_range[share.detect_color][1])
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones(
                        (6, 6), np.uint8))  # Opening (morphology)
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones(
                        (6, 6), np.uint8))  # Closing (morphology)
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL,
                                                cv2.CHAIN_APPROX_NONE)[-2]  # find countour
                    areaMaxContour, area_max = getAreaMaxContour(
                        contours)  # find the maximum countour
            if area_max > 2500:  # find the maximum area
                share.rect = cv2.minAreaRect(areaMaxContour)
                box = np.int0(cv2.boxPoints(share.rect))

                share.roi = getROI(box)  # get share.roi zone
                share.get_roi = True

                # get the center coordinates of block
                img_centerx, img_centery = getCenter(
                    share.rect, share.roi, share.size, square_length)
                share.world_x, share.world_y = convertCoordinate(
                    img_centerx, img_centery, share.size)  # convert to world coordinates

                cv2.drawContours(img, [box], -1, share.range_rgb[share.detect_color], 2)
                cv2.putText(img, '(' + str(share.world_x) + ',' + str(share.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, share.range_rgb[share.detect_color], 1)  # draw center position
                # compare the last coordinate to determine whether to move
                distance = math.sqrt(pow(share.world_x - share.last_x, 2) +
                                     pow(share.world_y - share.last_y, 2))
                share.last_x, share.last_y = share.world_x, share.world_y
                share.track = True

                # cumulative judgment
                if share.action_finish:
                    if distance < 0.3:
                        share.center_list.extend((share.world_x, share.world_y))
                        share.count += 1
                        if share.start_count_t1:
                            share.start_count_t1 = False
                            share.t1 = time.time()
                        if time.time() - share.t1 > 1.5:
                            share.rotation_angle = share.rect[2]
                            share.start_count_t1 = True
                            share.world_X, share.world_Y = np.mean(
                                np.array(share.center_list).reshape(share.count, 2), axis=0)
                            share.count = 0
                            share.center_list = []
                            share.start_pick_up = True
                    else:
                        share.t1 = time.time()
                        share.start_count_t1 = True
                        share.count = 0
                        share.center_list = []
        return share


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
