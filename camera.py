#! python3
# -*- encoding: utf-8 -*-
'''
@File   		:   camera.py
@Time    		:   2021/07/06 18:23:30
@Author  		:   ZXW2600
@Version 		:   1.0
@Contact 		:   zhaoxiwnei74@gmail.com
@description	:   相机拍照及视觉处理
'''
import cv2
import numpy as np


def pointInRectangle(point, rectangle):
    x, y, w, h = rectangle
    if (point[0] > x and point[0] < w+x) and (point[1] > y or point[1] < h+y):
        return 1
    elif (point[0] < x or point[0] < w+x) or (point[1] < y or point[1] > h+y):
        return -1
    else:
        return 0


class Camera:
    def __init__(self, camera_index):
        self.threshold = 50
        self.method = 0
        self.source = 0
        self.adaptiveThreshold_block = 601
        self.adaptiveThreshold_C = 30

        self.width_start = 0
        self.width_stop = 1080
        self.height_start = 0
        self.height_stop = 720

        cv2.namedWindow("threshold")
        cv2.createTrackbar("threshold", "threshold", 0,
                           255, self.threshold_callback)
        cv2.createTrackbar("block", "threshold", 0,
                           500, self.adaptive_threshold_block_callback)
        cv2.createTrackbar("C", "threshold", 0,
                           100, self.adaptive_threshold_C_callback)
        cv2.createTrackbar("method", "threshold", 0, 2, self.method_callback)
        cv2.createTrackbar("source", "threshold", 0, 1, self.source_callback)

        self.camera = cv2.VideoCapture(camera_index)
        self.camera.set(3, 1080)  # width=1920
        self.camera.set(4, 720)  # height=1080

        cv2.namedWindow("ROI")

        cv2.createTrackbar("width start", "ROI", 0, 1080, self.wstart_callback)
        cv2.createTrackbar("width stop", "ROI", 0, 1080, self.wstop_callback)
        cv2.createTrackbar("height start", "ROI", 0, 720, self.hstart_callback)
        cv2.createTrackbar("height stop", "ROI", 0, 720, self.hstop_callback)

    def wstart_callback(self, aim):
        if aim < self.width_stop:
            self.width_start = aim

    def wstop_callback(self, aim):
        if aim > self.width_start:
            self.width_stop = aim

    def hstart_callback(self, aim):
        if aim<self.width_stop:
            self.height_start = aim

    def hstop_callback(self, aim):
        if aim>self.width_start:
            self.height_stop = aim

    def threshold_callback(self, threshold):
        self.threshold = threshold

    def adaptive_threshold_C_callback(self, threshold):
        self.adaptiveThreshold_C = threshold

    def adaptive_threshold_block_callback(self, threshold):
        self.adaptiveThreshold_block = threshold*2+3

    def method_callback(self, method):
        self.method = method

    def source_callback(self, source):
        self.source = source

    def takeAndWritePicture(self, object_tag=""):
        """[拍照并检测物体位置]
        Args:
            object_tag ([type]): [标签]
        """
        _, pic = self.camera.read()
        pic=pic[self.height_start:self.height_stop,self.width_start:self.width_stop]
        if self.source == 0:
            pic_gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        if self.source == 1:
            pic_hsv = cv2.cvtColor(pic, cv2.COLOR_BGR2HSV)
            pic_h = cv2.split(pic_hsv)[0]  # H通道
            pic_s = cv2.split(pic_hsv)[1]  # S通道
            pic_v = cv2.split(pic_hsv)[2]  # V通道
            pic_gray = 255-pic_s
        if(self.method == 0):
            pic_threshold = cv2.adaptiveThreshold(pic_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                  cv2.THRESH_BINARY, self.adaptiveThreshold_block, self.adaptiveThreshold_C)
            pic_threshold = 255-pic_threshold

        if(self.method == 1):
            ret, pic_threshold = cv2.threshold(
                pic_gray, self.threshold, 255, cv2.THRESH_BINARY_INV)

        if(self.method == 2):
            ret, pic_threshold = cv2.threshold(
                pic_gray, self.threshold, 255, cv2.THRESH_OTSU)
            pic_threshold = 255-pic_threshold
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        pic_open = cv2.morphologyEx(pic_threshold, cv2.MORPH_OPEN, kernel)
        cv2.imshow("open", pic_open)
        sp = pic.shape
        height = sp[0]  # height(rows) of image
        width = sp[1]  # width(colums) of image
        points = [(0, 0), (width, 0), (0, height), (width, height)]

        contours, hier = cv2.findContours(
            pic_open, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_value = []
        area = []
        for cidx, cnt in enumerate(contours):
            if pointInRectangle(points[0], cv2.boundingRect(cnt)) == -1 and\
                    pointInRectangle(points[1], cv2.boundingRect(cnt)) == -1 and\
                    pointInRectangle(points[2], cv2.boundingRect(cnt)) == -1 and\
                    pointInRectangle(points[3], cv2.boundingRect(cnt)) == -1:
                contours_value.append(cnt)
                area.append(cv2.contourArea(cnt))

        pic_tag = np.copy(pic)
        x, y, w, h = 0, 0, 0, 0
        if len(area):
            max_idx = np.argmax(area)
            max_countour = contours_value[max_idx]
            max_rectangle = cv2.boundingRect(max_countour)
            cv2.rectangle(pic_tag, max_rectangle, (255, 0, 0), 2)
            x, y, w, h = max_rectangle
            cv2.putText(pic_tag, object_tag, (x, y),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
            ret = True
        else:
            ret = False

        return ret, pic, pic_tag, x, y, w, h


if __name__ == "__main__":
    demo = Camera(0)
    while True:
        ret, pic, pic_tag, x_1, y_1, w_1, h_1 = demo.takeAndWritePicture(
            "demo")
        cv2.imshow("test", pic_tag)
        # cv2.imwrite("000.png", pic)
        cv2.waitKey(1)
