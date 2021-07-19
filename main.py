#! python3
# -*- encoding: utf-8 -*-
'''
@File   		:   main.py
@Time    		:   2021/07/08 11:38:40
@Author  		:   ZXW2600
@Version 		:   1.0
@Contact 		:   zhaoxiwnei74@gmail.com
@description	:   自动采集数据主程序
'''

from numpy.lib.type_check import imag
from camera import Camera
from image_voc import image_voc
from scservo_sdk import SCSController
import cv2
from enum import Enum
import time


"""初始化设备"""
index_image = int(input("请输入开始的图片序号:"))
tag_name = input("请输入本次采集的物品tag：")


"""创建舵机控制器"""
servo = SCSController("/dev/ttyUSB0", 115200)
servo.init()
"""转盘位置归零"""
servo.setAcc(1, 0)
servo.setAcc(2, 0)
servo.WritePosition(1, 2047)
servo.WritePosition(2, 0)


def servo_set_low_speed():
    servo.setSpeed(2, 600)
    servo.setSpeed(1, 600)
    servo.setAcc(1, 0)
    servo.setAcc(2, 0)


def servo_set_high_speed():
    servo.setSpeed(2, 0)
    servo.setSpeed(1, 0)
    servo.setAcc(1, 0)
    servo.setAcc(2, 0)


"""创建相机"""
camera = Camera(2)


"""转盘转动角度范围"""
angle0_min = 0
angle0_max = 360

angle0_min_servo = 0
angle0_max_servo = 4096

angle1_min = 0
angle1_max = 60

angle1_min_servo = 2047
angle1_max_servo = int(2047-60/360*4096)

angle_step = 10
angle_step_servo = int(10/360*4096)

"""状态设置"""


class State(Enum):
    INIT = 0
    PAUSE = 1
    RUNNING = 2
    STOP = 3
    EXIT = 4
    WAIT = 5


g_state = State.WAIT


"""参数设置回调函数"""
# 滑动条回调


def angle0_callback(angle):
    global servo
    global angle0_max
    global angle0_max_servo
    servo.WritePosition(2, int(angle/360*4096))
    angle0_max = angle
    angle0_max_servo = int(angle/360*4096)


def angle1_min_callback(angle):
    global servo
    global angle1_min
    global angle1_min_servo
    angle1_min = angle
    servo.WritePosition(1, int(2047+angle/360*4096))
    angle1_min_servo = int(2047+angle/360*4096)


def angle1_max_callback(angle):
    global angle1_max
    global angle1_max_servo
    global servo
    angle1_max = angle
    servo.WritePosition(1, int(2047+angle/360*4096))
    angle1_max_servo = int(2047+angle/360*4096)


def angle_step_callback(angle):
    global angle_step
    global angle_step_servo
    angle_step = angle
    angle_step_servo = int(angle/360*4096)
# 按钮回调


def start_button_callback(*args):
    global g_state
    g_state = State.INIT


def stop_button_callback(*args):
    global g_state
    g_state = State.STOP


def pause_button_callback(*args):
    global g_state
    if g_state is State.RUNNING:
        g_state = State.PAUSE
    elif g_state is State.PAUSE:
        g_state = State.RUNNING


def exit_button_callback(*args):
    global g_state
    g_state = State.EXIT


"""交互界面回调函数"""
cv2.namedWindow("setting")
cv2.namedWindow("Real-time view", 1)
cv2.resizeWindow("Real-time view", 800, 600)  # 修改窗口大小为960X720

cv2.createTrackbar("dial angle", "setting", 0, 360, angle0_callback)
cv2.createTrackbar("camera-angle-low", "setting", 0, 90, angle1_min_callback)
cv2.createTrackbar("camera-angle-high", "setting", 0, 90, angle1_max_callback)
cv2.createTrackbar("angle_step", "setting", 0, 60, angle_step_callback)
cv2.createButton("start", start_button_callback)
cv2.createButton("pause", pause_button_callback)
cv2.createButton("stop", stop_button_callback)
cv2.createButton("exit", exit_button_callback)


cv2.waitKey(1)  # 刷新界面

angle0 = angle0_min_servo
angle1 = angle1_min_servo

# 程序主逻辑循环
while g_state is not State.EXIT:
    # 初始化舵机转角
    if g_state is State.INIT:
        angle0 = angle0_min_servo
        angle1 = angle1_min_servo
        servo.WritePosition(2, angle0)
        servo.WritePosition(1, angle1)
        servo_set_high_speed()
        time.sleep(2)
        servo_set_low_speed()
        g_state = State.RUNNING

    # 采集照片并显示
    ret, pic, pic_tag, xmin, ymin, width, height = camera.takeAndWritePicture(
        tag_name)
    cv2.imshow("Real-time view", pic_tag)
    key = cv2.waitKey(1)

    if key == 113:
        exit_button_callback()
    if key == 97:
        start_button_callback()
    if key == 115:
        stop_button_callback()

    # 保存照片和标注
    if g_state is State.RUNNING:
        image = image_voc()
        image.addImage(pic)
        if ret is True:
            image.addAnnotation(tag_name, xmin, ymin, width, height)
        image.writeFile(index_image)
        index_image += 1

        # 更新舵机转角
        if angle0 <= angle0_max_servo:
            angle0 += angle_step_servo
        else:
            angle1 += angle_step_servo
            angle0 = angle0_min_servo
            print("one turn finished!")
            servo.WritePosition(2, angle0)
            servo.WritePosition(1, angle1)
            servo_set_high_speed()
            time.sleep(2)
            servo_set_low_speed()

        if angle1 > angle1_max_servo:
            g_state = State.STOP
            print("all finished! stop!")
        servo.WritePosition(2, angle0)
        servo.WritePosition(1, -angle1)
        time.sleep(0.2)


"""外设收尾"""
servo.Close()
