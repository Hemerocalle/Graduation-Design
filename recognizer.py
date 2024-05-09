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
from cv2 import VideoCapture
from cv2.typing import MatLike as CVImage
import numpy as np
from PyQt5.QtWidgets import QFileDialog

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
            image = np.fromfile(path, dtype=np.uint8)
            image = cv2.imdecode(image, -1)
            if image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        except FileNotFoundError:  # 找不到图片
            return Result.FILE_NOT_FOUND, _

        # 将图像展示在屏幕上
        cls.img_origin = image
        cv2.imwrite(PATH_ORIGIN, image)
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
    vidio_origin: VideoCapture
    vidio_index: int
    emotions: list[tuple]
    emotion_freq: int

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
        cls.vidio_origin = VideoCapture()  # 视频流
        ret = cls.vidio_origin.open(path)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
        if ret is False:
            return Result.FILE_NOT_FOUND, _

        # 将视频的第一帧展示在屏幕上
        cv2.waitKey(1)
        cls.vidio_index = 0
        cls.emotion_freq = 0
        _, frame = cls.vidio_origin.read()  # 从视频流中读取
        cv2.imwrite(PATH_ORIGIN, frame)
        return Result.FINISH, path

    @classmethod
    def detectImg(cls) -> tuple[Result, str]:
        cv2.waitKey(1)
        # 从视频中切分出图像信息
        cls.vidio_origin.set(cv2.CAP_PROP_POS_FRAMES, cls.vidio_index)
        ret, frame = cls.vidio_origin.read()
        cls.vidio_index += 3
        if ret is False:
            return Result.FINISH, ''
        # cv2.imwrite(PATH_ORIGIN, frame)

        # 提高视频流畅程度，每识别一帧会冷却3帧
        if cls.emotion_freq != 0:
            cls.emotion_freq -= 1
        else:
            cls.emotion_freq = 3
            # 获取灰度图像
            # img_gray = cv2.imread(PATH_ORIGIN, 0)
            img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # 识别人脸位置
            faces = cls.getFace(img_gray)
            if len(faces) == 0:  # 找不到人脸
                cv2.imwrite(PATH_RESULT, frame)
                return Result.FACE_NOT_FOUND_CONTINUE, ''

            # 识别表情状态
            cls.emotions = cls.getEmotion(img_gray, faces)

        # 将识别结果展示在屏幕图像框中
        result, text = cls.markEmotion(frame, cls.emotions)
        cv2.imwrite(PATH_RESULT, result)
        # cv2.imwrite('file_temp/vedio_res.png', cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

        return Result.CONTINUE, text


# 实时识别器
class RecCamera(Recognizer):
    camera: VideoCapture
    emotions: list[tuple]
    emotion_freq: int

    @classmethod
    def radioOn(cls):
        print('radio 3 on')
        cls.camera = VideoCapture()  # 视频流

    @classmethod
    def radioOff(cls):
        print('radio 3 off')
        cls.camera.release()  # 释放视频流

    @classmethod
    def loadImg(cls, flag=Result.PREPARE) -> tuple[Result, str]:
        if flag is Result.PREPARE:
            return Result.LOADING, ''

        ret = cls.camera.open(0)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
        if ret is False:
            return Result.CAMERA_NOT_FOUND, ''

        cv2.waitKey(1)
        cls.emotion_freq = 0
        _, cover = cls.camera.read()  # 从视频流中读取
        cover = cv2.flip(cover, 1)
        cv2.imwrite(PATH_ORIGIN, cover)
        # cls.timer.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
        return Result.CAMERA_START, ''

    @classmethod
    def detectImg(cls) -> tuple[Result, str]:
        cv2.waitKey(1)
        # 从视频流中读取
        ret, frame = cls.camera.read()
        if ret is False:
            return Result.FINISH, ''
        frame = cv2.flip(frame, 1)
        # cv2.imwrite(PATH_ORIGIN, frame)

        # 提高视频流畅程度，每识别一帧会冷却3帧
        if cls.emotion_freq != 0:
            cls.emotion_freq -= 1
        else:
            cls.emotion_freq = 3
            # 获取灰度图像
            # img_gray = cv2.imread(PATH_ORIGIN, 0)
            img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # 识别人脸位置
            faces = cls.getFace(img_gray)
            if len(faces) == 0:  # 找不到人脸
                cv2.imwrite(PATH_RESULT, frame)
                return Result.FACE_NOT_FOUND_CONTINUE, ''

            # 识别表情状态
            cls.emotions = cls.getEmotion(img_gray, faces)

        # 将识别结果展示在屏幕图像框中
        result, text = cls.markEmotion(frame, cls.emotions)
        cv2.imwrite(PATH_RESULT, result)
        return Result.CONTINUE, text
