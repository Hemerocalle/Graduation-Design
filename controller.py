# -*- coding: utf-8 -*-

# 基于机器视觉的人脸表情识别系统设计-汪哲文毕业设计
#
# controller.py
# 本文件为控制层，负责接收表现层的数据，将工作指令转发给正确的逻辑执行机构
# 并将逻辑层反馈的数据传递回表现层
#
# Controller
# 识别器的控制器，用于对外提供接口并协调三个识别器的工作状态
#
# radio_set
# 根据给定的索引设置语音识别器类型，并相应地更新用户界面状态
#
# prepare
# 初始化和重置界面元素状态以准备开始任务
#
# loadImg
# 根据当前模型状态加载图像，处理图像加载过程中的各种结果
# 并更新UI状态来反映加载结果
#
# detectImg
# 识别图像中的人脸并进行相应处理
#
# 最后更新时间 2024/05/17

from PyQt5.QtWidgets import QLabel, QPushButton

from data import Result, RECOGNIZER_TYPE, PATH_RESULT, PATH_ORIGIN
from framework import AbstractRecognizer
from recognizer import RecImage, RecVidio, RecCamera


# 识别器的控制器，用于对外提供接口并协调三个识别器的工作状态
class Controller():
    _instance = None
    mode: tuple[type]
    rec: AbstractRecognizer  # 其实是 TypeVar[Base] ,但是反正是静态无所谓了
    enable: dict[str, bool]
    imageBox: QLabel
    textBox: QLabel
    startButton: QPushButton

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kw)
        return cls._instance

    @classmethod
    def __init__(cls, mode=(RecImage, RecVidio, RecCamera), index=0) -> None:
        cls.mode = mode
        cls.rec: AbstractRecognizer = mode[index]
        cls.rec.radioOn()
        cls.enable = {'model': False, 'image': False}

    # 根据给定的索引设置语音识别器类型，并相应地更新用户界面状态
    @classmethod
    def radio_set(cls, index: str) -> None:
        if type(cls.rec) is cls.mode[RECOGNIZER_TYPE[index]]:
            return

        # 根据索引设置新的识别器类型
        cls.rec = cls.mode[RECOGNIZER_TYPE[index]](cls.rec)
        cls.enable['image'] = False
        if cls.enable['model'] is False:
            return

        # 更新用户界面显示
        cls.textBox.setText('数据框')
        cls.imageBox.setStyleSheet('border: 3px solid black;')
        cls.imageBox.setText('图像框')
        cls.startButton.setEnabled(all(cls.enable.values()))

    # 初始化和重置界面元素状态以准备开始任务
    @classmethod
    def prepare(cls, prepareButton: QPushButton, startButton: QPushButton,
                imageBox: QLabel, textBox: QLabel) -> None:
        # 启用模型并设置界面元素
        cls.enable['model'] = True
        cls.imageBox = imageBox
        cls.textBox = textBox
        cls.startButton = startButton
        cls.startButton.setEnabled(all(cls.enable.values()))
        prepareButton.setEnabled(False)
        cls.textBox.setText(Result.PREPARE.value)

    # 根据当前模型状态加载图像，处理图像加载过程中的各种结果
    # 并更新UI状态来反映加载结果
    @classmethod
    def loadImg(cls) -> None:
        if cls.enable['model'] is False:  # 检查模型是否已载入，未载入则直接返回
            return
        res, text = cls.rec.loadImg()  # type: ignore

        # 根据加载图像的结果更新UI状态
        if res is Result.FINISH:  # 图像加载完成
            cls.enable['image'] = True
            cls.textBox.setText(text)
            cls.imageBox.setStyleSheet(f'image: url(./{PATH_ORIGIN})')
            cls.imageBox.setText('')
        elif res is Result.NO_FILE_SELECTED:  # 未选择文件
            cls.enable['image'] = False
            cls.textBox.setText(Result.NO_FILE_SELECTED.value)
            cls.imageBox.setStyleSheet('border: 3px solid black;')
            cls.imageBox.setText('图像框')
        elif res is Result.FILE_NOT_FOUND:  # 找不到文件
            cls.enable['image'] = False
            cls.textBox.setText(Result.FILE_NOT_FOUND.value)
            cls.imageBox.setStyleSheet('border: 3px solid black;')
            cls.imageBox.setText('图像框')
        elif res is Result.LOADING:  # 请等待
            cls.textBox.setText(Result.LOADING.value)
            # 重新尝试加载图像
            res, text = cls.rec.loadImg(Result.LOADING)  # type: ignore
            if res is Result.CAMERA_START:
                cls.enable['image'] = True
                cls.textBox.setText(Result.CAMERA_START.value)
                cls.imageBox.setStyleSheet(f'image: url(./{PATH_ORIGIN})')
                cls.imageBox.setText('')
            elif res is Result.CAMERA_NOT_FOUND:
                cls.enable['image'] = False
                cls.textBox.setText(Result.CAMERA_NOT_FOUND.value)
                cls.imageBox.setStyleSheet('border: 3px solid black;')
                cls.imageBox.setText('图像框')
        else:
            print('发生未知错误，可能是资源导入失败')
            cls.enable['image'] = False
            cls.textBox.setText('发生未知错误，可能是资源导入失败')
            cls.imageBox.setStyleSheet('border: 3px solid black;')
            cls.imageBox.setText('图像框')
        cls.startButton.setEnabled(all(cls.enable.values()))

    # 识别图像中的人脸并进行相应处理
    @classmethod
    def detectImg(cls) -> None:
        while cls.enable['image']:
            # 调用识别函数检测图像，获取结果和识别到的文本
            res, text = cls.rec.detectImg()  # type: ignore
            if cls.enable['image'] is False:  # 如果检测到瞬间的页面切换，则退出
                return
            if res is Result.FINISH:  # 识别完成，停止工作
                cls.textBox.setText(text)
                cls.imageBox.setStyleSheet(f'image: url(./{PATH_RESULT})')
                break
            elif res is Result.CONTINUE:  # 识别完成，继续工作
                cls.textBox.setText(text)
                cls.imageBox.setStyleSheet(f'image: url(./{PATH_RESULT})')
            elif res is Result.FACE_NOT_FOUND:  # 找不到人脸，停止工作
                cls.textBox.setText(Result.FACE_NOT_FOUND.value)
                break
            elif res is Result.FACE_NOT_FOUND_CONTINUE:  # 找不到人脸，继续工作
                cls.textBox.setText(Result.FACE_NOT_FOUND_CONTINUE.value)
                cls.imageBox.setStyleSheet(f'image: url(./{PATH_RESULT})')
            else:
                print('发生未知错误，可能是识别器无法正常工作')
                cls.textBox.setText('数据框')
                cls.imageBox.setStyleSheet('border: 3px solid black;')
                cls.imageBox.setText('图像框')
                break
        cls.startButton.setEnabled(all(cls.enable.values()))


controller = Controller()
