#!/usr/bin/env python3
import os  # nopep8
import sys  # nopep8
fpath = os.path.join(os.path.dirname(__file__), os.pardir)  # nopep8
sys.path.insert(0, fpath)  # nopep8

from picarx import Picarx
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import logging
import math
import time


def region_of_interest(image):
    # Get dimension
    height, width = image.shape

    # Create a polygon for the bottom half of the screen
    polygon = np.array([[(0, height * 1 / 2), (width, height * 1 / 2),
                       (width, height), (0, height), ]], np.int32)

    # Create mask
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygon, 255)

    # Apply mask
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image


def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    # Copy frame
    line_frame = np.copy(frame)

    # Draw lines
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_frame, (x1, y1), (x2, y2), line_color, line_width)

    return line_frame


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5):
    # Copy frame
    heading_image = np.copy(frame)

    # Get dimension
    height, width, _ = frame.shape

    # Compute line
    steering_angle_radian = np.deg2rad(steering_angle)
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 + height / 2 * math.tan(steering_angle_radian))
    y2 = int(height / 2)

    # Draw line
    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)

    return heading_image


def camera_feedback(frame, plot=False):
    if plot:
        cv2.imshow('frame', frame)

    # Apply Gaussian blur
    blur = cv2.GaussianBlur(frame, (25, 25), 0)
    if plot:
        cv2.imshow('blur', blur)

    # Convert to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    if plot:
        cv2.imshow('hsv', hsv)

    # Select color
    lower_blue = np.array([65, 0, 0])
    upper_blue = np.array([105, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    if plot:
        cv2.imshow('mask', mask)

    # Morphology operations
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    if plot:
        cv2.imshow('opening', opening)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    if plot:
        cv2.imshow('closing', closing)

    # Crop ROI
    cropped_closing = region_of_interest(closing)
    if plot:
        cv2.imshow('cropped_closing', cropped_closing)

    # Detect contours
    contours, _ = cv2.findContours(cropped_closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big_contour = max(contours, key=cv2.contourArea)

    contours_img = np.copy(frame)
    cv2.drawContours(contours_img, [big_contour], 0, (0, 0, 255), 2)
    if plot:
        cv2.imshow('contours_img', contours_img)

    # Compute steering
    M = cv2.moments(big_contour)
    cx = M['mu20']/M['m00']
    cy = M['mu02']/M['m00']
    cxy = M['mu11']/M['m00']
    steering_angle = np.round(1/2*np.arctan(2*cxy/(cx-cy)))

    final_frame = display_heading_line(frame, steering_angle)
    logging.info('steering_angle: %d' % steering_angle)
    cv2.imshow("final_frame", final_frame)

    return steering_angle


def test_photo(file):
    # Load photo
    frame = np.load(file)

    camera_feedback(frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# test_photo('image.npy')

px = Picarx()
px.set_camera_servo2_angle(-40)
steering_angle = 0

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=camera.resolution)
time.sleep(2)

input('Ready?')
px.turn(0)
px.run(50)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    steering_angle_current = camera_feedback(frame)
    steering_angle = steering_angle*0.9 + steering_angle_current*0.1
    px.turn(np.round(steering_angle))
    rawCapture.truncate(0)   # Release cache

    k = cv2.waitKey(1) & 0xFF
    # 27 is the ESC key, which means that if you press the ESC key to exit
    if k == 27:
        break

px.stop()
cv2.destroyAllWindows()
camera.close()
