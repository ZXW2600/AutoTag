#! python3
# -*- encoding: utf-8 -*-
'''
@File   		:   autoTag.py
@Time    		:   2021/07/06 18:23:30
@Author  		:   ZXW2600
@Version 		:   1.0
@Contact 		:   zhaoxiwnei74@gmail.com
@description	:   相机拍照及视觉处理
'''
import cv2
import numpy as np

camera = cv2.VideoCapture(2)
while True:
    _, pic = camera.read()
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
    area=[]
    for cidx, cnt in enumerate(contours):
        if cv2.pointPolygonTest(cnt, points[0], False) == -1 and\
                cv2.pointPolygonTest(cnt, points[1], False) == -1 and\
                cv2.pointPolygonTest(cnt, points[2], False) == -1 and\
                cv2.pointPolygonTest(cnt, points[3], False) == -1:
            contours_value.append(cnt)
            area.append(cv2.contourArea(cnt))

    if len(area):
        max_idx = np.argmax(area)
        max_countour=contours_value[max_idx]
        max_rectangle=cv2.boundingRect(max_countour)
        cv2.rectangle(pic,max_rectangle,(255,0,0),2)
    
    cv2.imshow("demo", pic)
    cv2.imshow("threshold", pic_threshold)
    cv2.imshow("open", pic_open)

    cv2.waitKey(1)
