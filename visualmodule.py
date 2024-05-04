# -*- coding: utf-8 -*-

# 基于机器视觉的人脸表情识别系统设计-汪哲文毕业设计
#
# transform.py
# 本文件为逻辑层，负责通用逻辑执行
#
# Template
# 识别器的模板，用于提供识别器切换流程和通用视觉模块
#
# getFace
# 从灰度图像中找出人脸
#
# getEmotion
# 根据人脸检测结果切割图片，并识别为表情信息
#
# markEmotion
# 将表情信息添加到图像上，同时整理成文本信息
#
# uint2float
# 将图片从uint_8矩阵转化为float32矩阵，便于识别器处理
#
# putTextbyChinese
# 在图片上添加中文
# cv库无法执行此工作，需要将图片转为PIL文件，添加完成后再转回去
#
# 最后更新时间 2024/04/15

from typing import Sequence
from PIL import Image as PILImage, ImageDraw
import cv2
from cv2.typing import MatLike as CVImage, Rect
from cv2 import COLOR_BGR2RGB, COLOR_RGB2BGR
import numpy as np
from numpy._typing import NDArray as NPImage

from data import Result, CLASSIFIER_FACE, CLASSIFIER_EMOTION, CLASSIFIER_EMOTION_SIZE, EMOTION_LABELS, FONT
from framework import AbstractRecognizer


# 识别器的模板，用于提供识别器切换流程和通用视觉模块
class Recognizer(AbstractRecognizer):

    def __init__(self, rec: 'Recognizer') -> None:
        if (rec != None):
            rec.radioOff()
            self.radioOn()

    # 从灰度图像中找出人脸
    @classmethod
    def getFace(cls, image: CVImage) -> Sequence[Rect]:
        result = CLASSIFIER_FACE.detectMultiScale(image, 1.3, 5)
        return result

    # 根据人脸检测结果切割图片，并识别为表情信息
    @classmethod
    def getEmotion(cls, image: CVImage, fases: Sequence[Rect]) -> list[tuple]:
        img_np = np.expand_dims(image, 2)  # 224*224*1
        result = []
        for x1, y1, width, height in fases:
            x2, y2 = x1 + width, y1 + height
            face = img_np[y1:y2, x1:x2]
            try:
                face = cv2.resize(face, CLASSIFIER_EMOTION_SIZE)
            except:
                continue
            face = cls.uint2float(face)
            face = np.expand_dims(face, 0)
            face = np.expand_dims(face, -1)
            emotion = CLASSIFIER_EMOTION.predict(face)  # type: ignore
            # label = np.max(emotion)
            label = np.argmax(emotion)
            confidence = int(emotion[0][label] * 100)  # 百分数
            result.append((label, confidence, x1, y1, x2, y2))
        return result

    # 将表情信息添加到图像上，同时整理成文本信息
    @classmethod
    def markEmotion(cls, image: CVImage,
                    emotions: list[tuple]) -> tuple[CVImage, str]:
        result = image
        if len(emotions) == 1:
            text = Result.FACE_FOUND_SINGLE.value
        else:
            emotions.sort(key=lambda x: x[2])
            text = Result.FACE_FOUND_MULTIPLE.value.format(len(emotions))
        try:
            for index, data, x1, y1, x2, y2 in emotions:
                label = f'{EMOTION_LABELS[index]} ({str(data)}%)   '
                cv2.rectangle(result, (x1, y1), (x2, y2), (0, 0, 255), 2)
                result = cls.putText_CN(result, label, (x1, y1))
                text += label
                print(label)
        except:
            print('发生未知错误，可能是中文字库调用失败')
        return result, text

    # 将图片从uint_8矩阵转化为float32矩阵，便于识别器处理
    @classmethod
    def uint2float(cls, x: NPImage) -> NPImage:
        x = x.astype('float32')
        x = x / 255.0
        x = x - 0.5
        x = x * 2.0
        return x

    # 在图片上添加中文
    @classmethod
    def putText_CN(cls, image: CVImage, text: str,
                   position: tuple[float, float]) -> CVImage:
        # 将OpenCV图像转换为PIL图像
        img_pil = PILImage.fromarray(cv2.cvtColor(image, COLOR_BGR2RGB))

        # 在PIL图像上绘制文本
        img_draw = ImageDraw.Draw(img_pil)
        img_draw.text(position, text, font=FONT,
                      fill=(255, 0, 0))  # PIL中颜色为RGB格式

        # 将PIL图像转换回OpenCV图像
        img_res = cv2.cvtColor(np.array(img_pil), COLOR_RGB2BGR)

        return img_res
