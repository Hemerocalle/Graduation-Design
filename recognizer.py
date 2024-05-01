# -*- coding: utf-8 -*-

# 基于机器视觉的人脸表情识别系统设计-汪哲文毕业设计
#
# recognizer.py
# 本文件为逻辑层，负责收到控制层工作指令后开始工作，并回报执行结果
#
# RecImage
# 图像识别器
#
# RecVidio
# 视频识别器
#
# RecCamera
# 实时识别器
#
# 最后更新时间 2024/04/15

import cv2
from cv2.typing import MatLike as CVImage
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer
from moviepy.editor import VideoFileClip

from data import Result, PATH_RESULT, PATH_ORIGIN
from visualmodule import Recognizer


# 图像识别器
class RecImage(Recognizer):
    img_origin: CVImage

    @classmethod
    def radioOn(cls) -> None:
        print('radio 1 on')

    @classmethod
    def radioOff(cls) -> None:
        print('radio 1 off')

    @classmethod
    def loadImg(cls) -> tuple[Result, str]:
        # 选择文件并获取图像路径
        path, _ = QFileDialog.getOpenFileName(None, 'open img', '',
                                              '*.png;*.jpg;;All Files(*)')
        print(path)
        if path == '':
            return Result.NO_FILE_SELECTED, _

        # 导入图像
        try:
            # cls.img_origin = cv2.imread(path)
            img_np = np.fromfile(path, dtype=np.uint8)
            cls.img_origin = cv2.imdecode(img_np, -1)
        except FileNotFoundError:  # 找不到图片
            return Result.FILE_NOT_FOUND, _

        # 将图像展示在屏幕上
        cv2.imwrite(PATH_ORIGIN, cls.img_origin)
        return Result.FINISH, path

    @classmethod
    def detectImg(cls) -> tuple[Result, str]:
        # 获取灰度图像
        img_gray = cv2.imread(PATH_ORIGIN, 0)

        # 识别人脸位置
        faces = cls.getFace(img_gray)
        if len(faces) == 0:  # 找不到人脸
            return Result.FACE_NOT_FOUND, ''

        # 识别表情状态
        emotions = cls.getEmotion(img_gray, faces)

        # 将识别结果展示在屏幕图像框中
        result, text = cls.markEmotion(cls.img_origin, emotions)
        cv2.imwrite(PATH_RESULT, result)
        return Result.FINISH, text


# 视频识别器
class RecVidio(Recognizer):
    vidio_origin: VideoFileClip
    vidio_duration: float
    vidio_index: float

    @classmethod
    def radioOn(cls):
        print('radio 2 on')

    @classmethod
    def radioOff(cls):
        print('radio 2 off')

    @classmethod
    def loadImg(cls) -> tuple[Result, str]:
        # 选择文件并获取视频路径
        path, _ = QFileDialog.getOpenFileName(None, 'open file', '',
                                              "*.avi;*.mp4;;All Files(*)")
        print(path)
        if path == '':
            return Result.NO_FILE_SELECTED, _

        # 导入视频
        try:
            # cls.vidio_origin = VideoFileClip(sys.argv[1]) # can be gif or movie
            cls.vidio_origin = VideoFileClip(path)
        except OSError:  # 找不到视频
            return Result.FILE_NOT_FOUND, _

        # 将视频的第一帧展示在屏幕上
        cls.vidio_index = 0
        cls.vidio_duration = cls.vidio_origin.duration
        frame = cls.vidio_origin.get_frame(0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(PATH_ORIGIN, frame)
        return Result.FINISH, path

    @classmethod
    def detectImg(cls):
        cv2.waitKey(1)
        # 从视频中切分出图像信息
        cls.vidio_index += 0.25
        if cls.vidio_index >= cls.vidio_duration:
            return Result.FINISH, Result.FINISH.value
        frame = cls.vidio_origin.get_frame(cls.vidio_index)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # cv2.imwrite(PATH_ORIGIN, frame)

        # 获取灰度图像
        # img_gray = cv2.imread(PATH_ORIGIN, 0)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # 识别人脸位置
        faces = cls.getFace(img_gray)
        if len(faces) == 0:  # 找不到人脸
            cv2.imwrite(PATH_RESULT, frame)
            return Result.FACE_NOT_FOUND_CONTINUE, ''

        # 识别表情状态
        emotions = cls.getEmotion(img_gray, faces)

        # 将识别结果展示在屏幕图像框中
        result, text = cls.markEmotion(frame, emotions)
        cv2.imwrite(PATH_RESULT, result)
        # cv2.imwrite('file_temp/vedio_res.png', cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

        return Result.CONTINUE, text


# 实时识别器
class RecCamera(Recognizer):

    @classmethod
    def radioOn(cls):
        print('radio 3 on')

    @classmethod
    def radioOff(cls):
        print('radio 3 off')

    @classmethod
    def loadImg(cls, flag=Result.PREPARE):
        print('radio 3 load')
        if flag is Result.PREPARE:
            return Result.LOADING, Result.LOADING

        cls.camera = cv2.VideoCapture()  # 视频流
        flag = cls.camera.open(0)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
        if flag == False:
            return Result.CAMERA_NOT_FOUND, Result.CAMERA_NOT_FOUND

        cls.img_num = 0
        cls.timer = QTimer()  # 定义定时器，用于控制显示视频的帧率 循环倒计时
        cls.timer.timeout.connect(cls.show_camera)  # 若定时器结束，则调用show_camera()

        _, cls.img_origin = cls.camera.read()  # 从视频流中读取
        cls.img_origin = cv2.flip(cls.img_origin, 1)
        cv2.imwrite(PATH_ORIGIN, cls.img_origin)
        # cls.timer.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
        return Result.CAMERA_START, Result.CAMERA_START

    @classmethod
    def detectImg(cls):
        cv2.waitKey(1)
        # 从视频流中读取
        _, frame = cls.camera.read()
        frame = cv2.flip(frame, 1)
        # cv2.imwrite(PATH_ORIGIN, frame)

        # 获取灰度图像
        # img_gray = cv2.imread(PATH_ORIGIN, 0)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # 识别人脸位置
        faces = cls.getFace(img_gray)
        if len(faces) == 0:  # 找不到人脸
            cv2.imwrite(PATH_RESULT, frame)
            return Result.FACE_NOT_FOUND_CONTINUE, ''

        # 识别表情状态
        emotions = cls.getEmotion(img_gray, faces)

        # 将识别结果展示在屏幕图像框中
        result, text = cls.markEmotion(frame, emotions)
        cv2.imwrite(PATH_RESULT, result)
        # cv2.imwrite('file_temp/vedio_res.png', cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

        return Result.CONTINUE, text

    @classmethod
    def show_camera(cls):

        flag, cls.image = cls.camera.read()  # 从视频流中读取
        show = cv2.resize(cls.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        cv2.imwrite('temp/camera.png', show)
