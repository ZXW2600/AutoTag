#! python3
# -*- encoding: utf-8 -*-
'''
@File   		:   image_voc.py
@Time    		:   2021/07/07 11:19:01
@Author  		:   ZXW2600 
@Version 		:   1.0
@Contact 		:   zhaoxiwnei74@gmail.com
@description	:   保存图片以及VOC的数据结构
'''

import cv2
from VOC import GEN_Annotations
class image_voc:
    def __init__(self):
        self.anno= GEN_Annotations()

    def addImage(self,image):
        self.image = image
        sp = image.shape
        height = sp[0]  # height(rows) of image
        width = sp[1]  # width(colums) of image
        channel = sp[2]
        self.anno.set_size(width,height,channel)


    def addAnnotation(self,tag_name,xmin,ymin,width,height):
        self.anno.add_pic_attr(tag_name,xmin,ymin,width,height)

    def writeFile(self,image_index):
        image_filename =str(image_index).zfill(6)+".png"
        annotation_filename =str(image_index).zfill(6)+".xml"
        cv2.imwrite(image_filename,self.image)
        self.anno.setImageFileName(image_filename)
        self.anno.savefile(annotation_filename)

if __name__ == "__main__":
    image= cv2.imread("000.png")
    demo_voc=image_voc()
    demo_voc.addImage(image)
    demo_voc.addAnnotation("demo_tag",0,0,2,2)
    demo_voc.writeFile(255)
