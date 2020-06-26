import numpy as np
import scipy.spatial.distance
import cv2
import imutils

import marker
import gui

BLUE_MIN = np.array([90, 40, 20])
BLUE_MAX = np.array([130, 255, 255])


def scan(image):
    "Scan an image for markers."
    image_blur = cv2.GaussianBlur(image, (15, 15), 0)

    image_hsv = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HSV)
    gui.show(image_hsv, "camera_hsv")

    mask = cv2.inRange(image_hsv, BLUE_MIN, BLUE_MAX)
    gui.show(mask, "mask_border")

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    markers = []

    mask_with_contours = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    image_with_contours = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    cv2.drawContours(mask_with_contours, contours, -1, (0, 255, 0), 2)
    cv2.drawContours(image_with_contours, contours, -1, (0, 255, 0), 2)

    gui.show(mask_with_contours, "mask_border_contours")
    gui.show(image_with_contours, "camera_border_contours")

    image_with_approx = image_with_contours.copy()

    for contour in contours:

        length = cv2.arcLength(contour, True)

        if length < 50:
            continue

        epsilon = 0.03*length
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) != 4:
            continue

        distances = []

        for i in range(len(approx)):
            point = approx[i]
            next = approx[(i+1) % 4]
            dist = scipy.spatial.distance.euclidean(point, next)
            distances.append(dist)

        maxDist = 0
        for dist in distances:
            if dist > maxDist:
                maxDist = dist

        for dist in distances:
            # Make sure polygons have reasonable dimensions
            if dist < 0.5*maxDist:
                break
        else:
            cv2.polylines(image_with_approx, [approx], True, (255, 0, 0), 2)
            markers.append(marker.Marker(
                [[int(coord) for coord in column[0]]
                 for column in approx]))

    gui.show(image_with_approx, "camera_border_approx")
    return markers
