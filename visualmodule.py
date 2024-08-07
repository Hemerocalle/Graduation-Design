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
# 从灰度图像中检测人脸
#
# getEmotion
# 为图像中每个面部区域检测表情
#
# markEmotion
# 在图像上标记表情信息，同时整理成文本信息
#
# microexpression
# 根据给定的情感原始值元组，计算并返回最显著的微表情及其置信度
#
# putText_CN
# 在图片上添加中文
# cv库无法执行此工作，需要将图片转为PIL文件，添加完成后再转回去
#
# uint2float
# 将图片从uint_8矩阵转化为float32矩阵，便于识别器处理
#
# 最后更新时间 2024/05/16

from math import floor
from PIL import Image as PILImage, ImageDraw
import cv2
from cv2.typing import MatLike as CVImage
from cv2 import COLOR_BGR2RGB, COLOR_RGB2BGR
import numpy as np
from numpy._typing import NDArray as NPImage

from data import Result, CLAHE_FACE, CLASSIFIER_FACE, CLASSIFIER_EMOTION, CLASSIFIER_EMOTION_SIZE, EMOTION_LABELS, EMOTION_MICRO_LABELS, EMOTION_MAP, FONT
from framework import AbstractRecognizer


# 识别器的模板，用于提供识别器切换流程和通用视觉模块
class Recognizer(AbstractRecognizer):

    def __init__(self, rec: 'Recognizer') -> None:
        if (rec != None):
            rec.radioOff()
            self.radioOn()

    # 从灰度图像中检测人脸
    @classmethod
    def getFace(cls, image: CVImage) -> list[tuple]:
        # image = cv2.GaussianBlur(image, (5, 5), 0)  # 高斯模糊
        # image = cv2.equalizeHist(image)  # 直方图均衡化
        image = CLAHE_FACE.apply(image)  # 局部对比度增强
        face = CLASSIFIER_FACE.detectMultiScale(image, 1.3, 5)

        # 移除眼睛、脖子等干扰数据
        result = []
        for x1, y1, size1, _ in face:
            for x2, y2, size2, _ in face:
                if size1 == size2:
                    continue

                # 检查是否有重叠
                if (x1 < x2 + size2 and x2 < x1 + size1 and y1 < y2 + size2
                        and y2 < y1 + size1 and size1 * 2 < size2):
                    break
            else:
                result.append((x1, y1, size1))
        return result

    # 为图像中每个面部区域检测表情
    @classmethod
    def getEmotion(cls, image: CVImage, fases) -> list[tuple]:
        img_np = np.expand_dims(image, 2)  # 224*224*1
        result = []
        for x1, y1, size in fases:
            x2, y2 = x1 + size, y1 + size
            face = img_np[y1:y2, x1:x2]
            try:
                face = cv2.resize(face, CLASSIFIER_EMOTION_SIZE)
            except:
                continue
            face = cls.uint2float(face)
            face = np.expand_dims(face, 0)
            face = np.expand_dims(face, -1)
            emotion = CLASSIFIER_EMOTION.predict(face)[0]  # type: ignore
            # print(emotion)
            # label = np.max(emotion)
            # label = np.argmax(emotion)
            # confidence = int(emotion[label] * 100)  # 百分数
            result.append((x1, y1, x2, y2, emotion))
        return result

    # 在图像上标记表情信息，同时整理成文本信息
    @classmethod
    def markEmotion(cls, image: CVImage,
                    emotions: list[tuple]) -> tuple[CVImage, str]:
        result = image
        if len(emotions) == 1:
            text = Result.FACE_FOUND_SINGLE.value
        else:
            emotions.sort(key=lambda x: x[0])
            text = Result.FACE_FOUND_MULTIPLE.value.format(len(emotions))
        try:
            for x1, y1, x2, y2, emotion in emotions:
                # label = f'{EMOTION_LABELS[index]} ({str(data)}%)   '
                # label = ','.join(f'{emotion[i]}' for i in range(7))
                label = cls.microexpression(emotion)
                cv2.rectangle(result, (x1, y1), (x2, y2), (0, 0, 255), 1)
                result = cls.putText_CN(result, label[:2], (x1, y1))
                text += label + '\n'
                print(label)
        except:
            print('发生未知错误，可能是中文字库调用失败')
        return result, text

    # 根据给定的情感原始值元组，计算并返回最显著的微表情及其置信度
    @classmethod
    def microexpression(cls, origin: tuple[int]) -> str:
        result = []
        confidence = 0
        emotions = tuple(EMOTION_MAP[i](origin[i]) for i in range(7))
        # print(origin)
        # print(emotions)
        limit = floor(0.85 * max(emotions))
        emotions = sorted(enumerate(emotions),
                          key=lambda x: x[1],
                          reverse=True)[:3]
        for i, value in emotions:
            if value < limit:
                break
            result.append(i)
            confidence += origin[i]

        # return tuple(EMOTION_MAP[i](origin[i]) for i in range(7))
        # return str(EMOTION_LABELS[result[-1]]) + f'{origin[result[-1]]*100:.0}'
        name = tuple(sorted(result))
        detail = tuple(EMOTION_LABELS[i] for i in result)
        return EMOTION_MICRO_LABELS[name].format(*detail,
                                                 round(confidence * 100))

    # 在图像上添加中文文本
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

    # 将图片从uint_8矩阵转化为float32矩阵，便于识别器处理
    @classmethod
    def uint2float(cls, x: NPImage) -> NPImage:
        x = x.astype('float32')
        x = x / 255.0
        x = x - 0.5
        x = x * 2.0
        return x
