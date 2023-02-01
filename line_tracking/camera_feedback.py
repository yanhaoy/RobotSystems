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


def average_slope_intercept(frame, line_segments):
    # Create line list
    lane_lines = []
    if line_segments is None:
        logging.info('No line segments detected')
        return lane_lines

    # Get shape
    _, width, _ = frame.shape

    # Init lists
    left_fit = []
    left_weight = []
    right_fit = []
    right_weight = []

    # Take 2/3 of the screen on each side
    boundary = 1/3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            # Skip vertical lines
            if x1 == x2:
                logging.info('Skipping vertical line segment (slope=inf): %s' % line_segment)
                continue

            # Compute line parameter
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            length = np.sqrt((x1-x2)**2 + (y1-y2)**2)

            # Determine left or right by slope
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
                    left_weight.append(length)
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))
                    right_weight.append(length)

    # Compute the weighted average
    left_fit_average = np.average(left_fit, axis=0, weights=left_weight)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    # Compute the weighted average
    right_fit_average = np.average(right_fit, axis=0, weights=right_weight)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines


def compute_steering_angle(frame, lane_lines):
    height, width, _ = frame.shape
    if not len(lane_lines) == 2:
        # Check lane number
        logging.info('Wrong lane number')
        return 0
    else:
        # Compute center
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.0
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # Compute steering angle
    y_offset = int(height / 2)
    steering_angle = np.rad2deg(math.atan(x_offset / y_offset))

    return steering_angle


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


def make_points(frame, line):
    # Get dimension
    height, width, _ = frame.shape

    # Get line parameter
    slope, intercept = line

    # Compute points
    y1 = height
    y2 = int(y1 * 1 / 2)
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))

    return [[x1, y1, x2, y2]]


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

    # Detect edges
    edges = cv2.Canny(closing, 100, 200)
    if plot:
        cv2.imshow('edges', edges)

    # Crop ROI
    cropped_edges = region_of_interest(edges)
    if plot:
        cv2.imshow('cropped_edges', cropped_edges)

    # Fit lines
    line_segments = cv2.HoughLinesP(cropped_edges, 1, np.pi / 180, 25, None, 50, 75)
    line_segment_image = display_lines(frame, line_segments)
    if plot:
        cv2.imshow("line_segment_image", line_segment_image)

    # Merge lines
    lane_lines = average_slope_intercept(frame, line_segments)
    lane_lines_image = display_lines(frame, lane_lines)
    if plot:
        cv2.imshow("lane_lines_image", lane_lines_image)

    # Compute steering
    steering_angle = compute_steering_angle(frame, lane_lines)
    final_frame = display_heading_line(lane_lines_image, steering_angle)
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
    steering_angle = steering_angle*0.5 + steering_angle_current*0.5
    px.turn(np.round(steering_angle))
    rawCapture.truncate(0)   # Release cache

    k = cv2.waitKey(1) & 0xFF
    # 27 is the ESC key, which means that if you press the ESC key to exit
    if k == 27:
        break

px.stop()
cv2.destroyAllWindows()
camera.close()
