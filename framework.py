# -*- coding: utf-8 -*-

# 基于机器视觉的人脸表情识别系统设计-汪哲文毕业设计
#
# framework.py
# 本文件为数据层，设计了三种识别器的框架，并提供了静态类型检查
#
# 最后更新时间 2024/04/15

from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QLabel, QPushButton, QFrame, QRadioButton

from data import Result


# 识别器的抽象基类，用于提供三种识别器的框架
class AbstractRecognizer(ABC):
    _instance = None

    def __new__(cls, _, *args, **kw):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kw)
        return cls._instance

    @abstractmethod
    def radioOn(cls) -> None:
        pass

    @abstractmethod
    def radioOff(cls) -> None:
        pass

    @abstractmethod
    def loadImg(cls) -> tuple[Result, str]:
        pass

    @abstractmethod
    def detectImg(cls) -> tuple[Result, str]:
        pass


# UI界面的类型检查辅助类
class Ui_Type_Check():
    lTitle: QLabel
    bPrepare: QPushButton
    bStart: QPushButton
    fType: QFrame
    rImage: QRadioButton
    rVidio: QRadioButton
    rCamera: QRadioButton
    lImage: QLabel
    lData: QLabel
