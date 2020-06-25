import math

import cv2 as cv2
import numpy as np

gap = 100
d_max_Length = 640
d_max_Width = 480
lineProximity = (122, 255, 123)
gapTop = (gap, gap)
gapBottom = (d_max_Length - gap, d_max_Width - gap)
temp = int(25)
myGaussianVector = (temp, temp)
thresholdingValue = 127


def grep(password=''):
    # capture is an instance of the library after it has successfully captured
    capture = cv2.VideoCapture(0)

    while capture.isOpened():
        # read image
        _, img = capture.read()

        # create a rectangle and mark the box in which the user is supposed to tae the input
        # We could also trim the window to that size
        cv2.rectangle(img, gapTop, gapBottom, lineProximity, 3)
        section = img[gap:d_max_Width - gap, gap:d_max_Length - gap]
        # section contains only the part of image we want

        # convert to GrayScale
        grey = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("GreyScale", grey)

        # applying gaussian blur
        value = myGaussianVector
        blurred = cv2.GaussianBlur(grey, value, 0)
        # cv2.imshow("Blurred", blurred)

        #
        # Thresholding part
        # noinspection PyRedeclaration
        _, thresh1 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_BINARY)
        # noinspection PyRedeclaration
        _, thresh2 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_BINARY_INV)
        # noinspection PyRedeclaration
        _, thresh3 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_TRUNC)
        # noinspection PyRedeclaration
        _, thresh4 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_TOZERO)
        # noinspection PyRedeclaration
        _, thresh5 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_TOZERO_INV)
        # noinspection PyRedeclaration
        _, thresh6 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_OTSU)
        # noinspection PyRedeclaration

        # # Our point of Interest
        _, thresh7 = cv2.threshold(blurred, thresholdingValue, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        global bg
        bg = thresh7.copy().astype("float")
        cv2.imshow('Binary', thresh1)
        cv2.imshow('Binary Inv', thresh2)
        cv2.imshow('Trunc', thresh3)
        cv2.imshow('Tozero', thresh4)
        cv2.imshow('Tozero inv', thresh5)
        cv2.imshow('Ostu\'s', thresh6)
        cv2.imshow('Modified Otsu', thresh7)

        # noinspection PyUnresolvedReferences
        (version, _, _) = cv2.__version__.split('.')

        contours = '1'
        if version == '3':
            image, contours, hierarchy = cv2.findContours(thresh7.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        elif version == '2':
            contours, hierarchy = cv2.findContours(thresh7.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find contour with max area
        cnt = max(contours, key=lambda x: cv2.contourArea(x))

        # create bounding rectangle around the contour
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(section, (x, y), (x + w, y + h), (0, 0, 255), 0)

        # finding convex hull
        hull = cv2.convexHull(cnt)

        # drawing contours
        drawing = np.zeros(section.shape, np.uint8)
        cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)

        # finding convex hull with return points = false
        hull = cv2.convexHull(cnt, returnPoints=False)

        # finding convexity defects
        defects = cv2.convexityDefects(cnt, hull)
        count_defects = 0
        cv2.drawContours(thresh7, contours, -1, (0, 255, 0), 3)

        # applying Cosine Rule to find angle for all defects (between fingers)
        # with angle > 90 degrees and ignore defects
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]

            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])

            # find length of all sides of triangle
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

            # apply cosine rule here
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

            # ignore angles > 90 and highlight rest with red dots
            if angle <= 70:
                count_defects += 1
                cv2.circle(section, far, 1, [0, 0, 255], -1)
            dist = cv2.pointPolygonTest(cnt, far, True)

            # draw a line from start to end i.e. the convex points (finger tips)
            # (can skip this part)
            cv2.line(section, start, end, [0, 255, 0], 2)
            cv2.circle(section, far, 5, [0, 0, 255], -1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(count_defects + 1), (70, 45), font, 1, (0, 0, 255), 2)
        cv2.putText(img, password, (70, 100), font, 1, (0, 0, 255), 2)
        cv2.imshow('Gesture', img)

        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            break
        elif k == 32:
            password += str(count_defects + 1)
            if len(password) == 4:
                break

    capture.release()
    cv2.destroyAllWindows()
    return password

grep()