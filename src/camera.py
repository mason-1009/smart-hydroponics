#!/usr/bin/env python3

import cv2
import numpy

class webcam(object):
    
    cameraObject = None
    imageData = None

    def __init__(self):
        # initiallize webcam
        self.cameraObject=cv2.VideoCapture(0)

    def getCameraFunctionality(self):
        return self.cameraObject.isOpened()

    def returnJPEGdata(self):
        return self.imageData

    def captureImage(self):
        # capture image and compress to JPEG
        ret,frame=self.cameraObject.read()
        ret,self.imageData=cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),90])

    def closeCamera(self):
        # destroy camera object
        self.cameraObject.release()
        cv2.destroyAllWindows()
