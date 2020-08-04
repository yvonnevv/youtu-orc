#encoding:utf-8  

import cv2
import os
from skimage.measure import compare_ssim

from config import splitDuration

def getPicFrame():
    videoDir = input('输入视频路径: ')
    path, filename = os.path.split(videoDir)

    if not filename.endswith(('.mp4', '.mkv', '.avi', '.wmv', '.iso')):
        print('视频格式不正确')
        return
    
    outputName = filename[0:-4]
    outputDir = './' + outputName
    frameOutputDir = outputDir + '/frames'

    if not(os.path.exists(outputDir)):
        os.mkdir(outputDir)
    if not(os.path.exists(frameOutputDir)):
        os.mkdir(frameOutputDir)

    vc = cv2.VideoCapture(videoDir) #读入视频文件  

    c = 1  
    
    if vc.isOpened(): #判断是否正常打开  
        rval , frame = vc.read()  
    else:  
        rval = False  

    timeF = vc.get(5) * splitDuration  #视频帧计数间隔频率 = 帧率 * 切片时间间隔  
    
    while rval:   #循环读取视频帧  
        rval, frame = vc.read()  
        if(c%timeF == 0): #每隔timeF帧进行存储操作  
            frame_h, frame_w, channels = frame.shape
            # frame_s = int(frame_h * ratio)
            word_area = frame[0:frame_h, 0:frame_w]
            cv2.imwrite(frameOutputDir+'/'+str(c).zfill(10) + '.jpg',word_area) #存储为图像  
        c = c + 1  
        cv2.waitKey(1)
    vc.release()
    return outputDir, frameOutputDir

def getPicFrameMain():
    outputDir, frameOutputDir = getPicFrame()
    print('------------ FINISH GET FRAMES ------------')
    print('frameOutputDir', frameOutputDir)
    return outputDir, frameOutputDir