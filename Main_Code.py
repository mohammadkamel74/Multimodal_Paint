############################## import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import speech_recognition as sr
import pyaudio
############################# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())
#################################### define the paint screen
img_1 = np.zeros([512,512,3],dtype=np.uint8)
img_1.fill(255)
#################################### define the lower and upper boundaries of the colors
redLower = (159, 50, 70)
redUpper = (180, 255, 255)
greenLower = (20, 100, 100)
greenUpper = (30, 255, 255)
#################################### define the microphone and related grammers
sr.Microphone.list_microphone_names()
mic = sr.Microphone(device_index=1)
r = sr.Recognizer()
counter_stop = 0
colors = ['red', 'blue', 'green', 'yello', 'white', 'black']

pts = deque()
ptsG= deque()

if not args.get("video", False):
    vs = VideoStream(src=0).start()
else:
    vs = cv2.VideoCapture(args["video"])

time.sleep(2.0)
speech ="red"

while True:
    key2 = cv2.waitKey(1) & 0xFF
    #################################### delete the screen
    if key2 == ord("x"):
        pts = []
        ptsG = []
        cv2.destroyAllWindows()
        img_1 = np.zeros([512, 512, 3], dtype=np.uint8)
        img_1.fill(255)
    #################################### speech mode to listen to the colors
    if key2 == ord("z"):
        #print("yes")
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Talk")
            audio_text = r.listen(source)
            try:
                speech=str(r.recognize_google(audio_text))
                if speech != "red":
                    if speech != "yellow":
                        speech = "red"
                print(speech)
            except:
                print("Sorry, I did not get that")

    # grab the current frame
    frame = vs.read()
    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    if speech =="red":
        mask = cv2.inRange(hsv, redLower, redUpper)
    elif speech =="yellow":
        mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
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
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
    # update the points queue
    if speech=="red":
        pts.append(center)
        #print(pts)
    if speech=="yellow":
        ptsG.append(center)
        #print(ptsG)
    if speech == "red":
    # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            #thickness = int(np.sqrt(args["buffer"] / float(1)) * 2.5)
            cv2.line(img_1, pts[i - 1], pts[i], (0, 0, 255), 2)
            #cv2.line(frame, ptsG[i - 1], ptsG[i], (0, 255, 0), 2)
    if speech == "yellow":
    # loop over the set of tracked points
        for i in range(1, len(ptsG)):
            # if either of the tracked points are None, ignore
            # them
            if ptsG[i - 1] is None or ptsG[i] is None:
                continue
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            #thickness = int(np.sqrt(args["buffer"] / float(1)) * 2.5)
            #cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), 2)
            cv2.line(img_1, ptsG[i - 1], ptsG[i], (25, 200, 200), 2)
    # show the frame to our screen
    sdsd = cv2.flip(img_1, 1)
    cv2.imshow("Frame", sdsd)
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()
# otherwise, release the camera
else:
    vs.release()
# close all windows
cv2.destroyAllWindows()