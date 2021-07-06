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
        self.camera = cv2.VideoCapture(2)

    def takeAndWritePicture(self, filename, object_tag):
        """[拍照并检测物体位置]
        Args:
            filename ([type]): [保存的文件名]
            object_tag ([type]): [标签]
        """
        _, pic = self.camera.read()
        pic_gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
        # pic_threshold=cv2.adaptiveThreshold(pic_gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,adaptiveThreshold_block,adaptiveThreshold_C)
        ret, pic_threshold = cv2.threshold(pic_gray, 125, 255, cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        pic_open = cv2.morphologyEx(pic_threshold, cv2.MORPH_OPEN, kernel)
        pic_open = 255-pic_open

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
            cv2.imwrite(filename, pic)
        else:
            ret = False

        return ret, pic_tag, x, y, w, h


if __name__ == "__main__":
    demo = Camera(2)
    while True:
        ret, pic, x_1, y_1, w_1, h_1 = demo.takeAndWritePicture(
            "000.png", "demo")
        cv2.imshow("test", pic)
        cv2.waitKey(1)
