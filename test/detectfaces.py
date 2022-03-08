#!/usr/bin/env python3

import cv2
import numpy

def formatFaceNumberString(faceCount):
    if faceCount == 0:
        return "No Faces"
    elif faceCount == 1:
        return "1 Face"
    else:
        return str(faceCount)+" Faces"

cameraDevice = cv2.VideoCapture(0)

# import facial cascade data
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

while True:

    # capture frame
    ret, frame = cameraDevice.read()
    
    # convert frame to grayscale for processing
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # find faces in image
    faces = faceCascade.detectMultiScale(grayFrame, 1.3, 5)

    # draw face rectangles
    for (x,y,w,h) in faces:
        print(str.format("Face detected at rectangle: ({},{}) -> ({},{})", x, y, x+w, x+y))
        frame = cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        cv2.putText(frame, formatFaceNumberString(len(faces)), (0,100), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255),2,cv2.LINE_AA)

    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cameraDevice.release()
cv2.destroyAllWindows()
