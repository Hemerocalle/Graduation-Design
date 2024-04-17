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
# 最后更新时间 2024/04/15

from PyQt5.QtWidgets import QLabel, QPushButton, QFrame, QRadioButton

from data import Result, RECOGNIZER_TYPE, PATH_RESULT, PATH_ORIGIN
from framework import AbstractRecognizer
from recognizer import RecImage, RecVidio, RecCamera


# 识别器的控制器，用于对外提供接口并协调三个识别器的工作状态
class Controller(AbstractRecognizer):
    mode: tuple[type]
    rec: AbstractRecognizer  # 其实是 TypeVar[Base] ,但是反正是静态无所谓了
    enable: dict[str, bool]
    imageBox: QLabel
    textBox: QLabel
    startButton: QPushButton

    @classmethod
    def __init__(cls, mode, index=0) -> None:
        cls.mode = mode
        cls.rec: AbstractRecognizer = mode[index]
        cls.rec.radioOn()
        cls.enable = {'model': False, 'image': False}

    # 切换模式
    @classmethod
    def radio_set(cls, index: str) -> None:
        if type(cls.rec) is cls.mode[RECOGNIZER_TYPE[index]]:
            return
        cls.rec = cls.mode[RECOGNIZER_TYPE[index]](cls.rec)
        cls.enable['image'] = False
        if cls.enable['model'] is False:
            return
        cls.textBox.setText('数据框')
        cls.imageBox.setStyleSheet('border: 3px solid black;')
        cls.imageBox.setText('图像框')
        cls.startButton.setEnabled(all(cls.enable.values()))

    # 模型载入
    @classmethod
    def prepare(cls, prepareButton: QPushButton, startButton: QPushButton,
                imageBox: QLabel, textBox: QLabel) -> None:
        cls.enable['model'] = True
        cls.imageBox = imageBox
        cls.textBox = textBox
        cls.startButton = startButton
        cls.startButton.setEnabled(all(cls.enable.values()))
        prepareButton.setEnabled(False)
        cls.textBox.setText(Result.PREPARE.value)

    # 资源导入
    @classmethod
    def loadImg(cls) -> None:
        if cls.enable['model'] is False:  # 如果没有载入模型则退出
            return
        res, text = cls.rec.loadImg()  # type: ignore
        if res is Result.FINISH:  # 导入完成
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
        else:
            print('发生未知错误，可能是资源导入失败')
            cls.enable['image'] = False
            cls.textBox.setText('发生未知错误，可能是资源导入失败')
            cls.imageBox.setStyleSheet('border: 3px solid black;')
            cls.imageBox.setText('图像框')
        cls.startButton.setEnabled(all(cls.enable.values()))

    # 开始识别
    @classmethod
    def detectImg(cls) -> None:
        while cls.enable['image']:
            res, text = cls.rec.detectImg()  # type: ignore
            if cls.enable['image'] is False:  # 如果瞬间切换页面则退出
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


controller = Controller((RecImage, RecVidio, RecCamera))
