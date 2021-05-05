# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time


class Object_Tracker:
    def __init__(self, colorRange, path=None, buffer=32):
        self.vs = VideoStream(src=0)
        self.path = path
        self.greenLower = tuple(colorRange[:3])
        self.greenUpper = tuple(colorRange[3:])
        self.buffer = buffer

        # initialize the list of tracked points, the frame counter,
        # and the coordinate deltas
        self.pts = deque(maxlen=buffer)
        self.counter = 0
        (self.dX, self.dY) = (0, 0)
        self.direction = ""

        if not path:
            self.vs.start()

        # otherwise, grab a reference to the video file
        else:
            self.vs = cv2.VideoCapture(path)

    # construct the argument parse and parse the arguments
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-v", "--video",
    # 	help="path to the (optional) video file")
    # ap.add_argument("-b", "--buffer", type=int, default=32,
    # 	help="max buffer size")
    # args = vars(ap.parse_args())

    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space

    def track_object(self):

        # if a video path was not supplied, grab the reference
        # to the webcam

        # allow the camera or video file to warm up
        # time.sleep(2.0)

        # keep looping
        while True:
            frame = self.vs.read()

            # handle the frame from VideoCapture or VideoStream
            frame = frame[1] if self.path else frame

            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if frame is None:
                return

            # resize the frame, blur it, and convert it to the HSV
            # color space
            frame = imutils.resize(frame, width=600)
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, self.greenLower, self.greenUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(
                mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cnts = imutils.grab_contours(cnts)
            center = None

            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then us
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    self.pts.appendleft(center)
                    print("appended")

            # loop over the set of tracked points
            for i in np.arange(1, len(self.pts)):
                print("read")
                # if either of the tracked points are None, ignore
                # them
                if self.pts[i - 1] is None or self.pts[i] is None:
                    continue

                # check to see if enough points have been accumulated in
                # the buffer
                if self.counter >= 10 and i == 1 and self.pts[-10] is not None:
                    # compute the difference between the x and y
                    # coordinates and re-initialize the direction
                    # text variables
                    self.dX = self.pts[-10][0] - self.pts[i][0]
                    self.dY = self.pts[-10][1] - self.pts[i][1]
                    (dirX, dirY) = ("", "")

                    # ensure there is significant movement in the
                    # x-direction
                    if np.abs(self.dX) > 20:
                        dirX = "East" if np.sign(self.dX) == 1 else "West"

                    # ensure there is significant movement in the
                    # y-direction
                    if np.abs(self.dY) > 20:
                        dirY = "North" if np.sign(self.dY) == 1 else "South"

                    # handle when both directions are non-empty
                    if dirX != "" and dirY != "":
                        self.direction = "{}-{}".format(dirY, dirX)

                    # otherwise, only one direction is non-empty
                    else:
                        self.direction = dirX if dirX != "" else dirY

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(self.buffer / float(i + 1)) * 2.5)
                cv2.line(frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

            # show the movement deltas and the direction of movement on
            # the frame
            cv2.putText(
                frame,
                self.direction,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                3,
            )
            cv2.putText(
                frame,
                "dx: {}, dy: {}".format(self.dX, self.dY),
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1,
            )

            key = cv2.waitKey(1) & 0xFF
            self.counter += 1

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

            cv2.imshow("frame", frame)

            # (flag, encodedImage) = cv2.imencode(".jpg", frame)

            # ensure the frame was successfully encoded
            # if not flag:
            # 	return

            # print('encodedImage')

    def __del__(self):
        print("destroyed")
        self.vs.stop()
        self.vs.release()
