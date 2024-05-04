# -*- coding: utf-8 -*-

# 基于机器视觉的人脸表情识别系统设计-汪哲文毕业设计
#
# main.py
# 本文件为表现层，负责启动用户交互界面，并将用户的操作汇报至控制层
#
# Window
# 在ui框架的基础上，连接信号和槽，完成数据传输
#
# 最后更新时间 2024/04/15

import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from framework import Ui_Type_Check
from controller import controller
from ui.ui import Ui_Form


class Window(QtWidgets.QMainWindow, Ui_Form, Ui_Type_Check):

    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)

        # 连接信号和槽
        self.bPrepare.clicked.connect(lambda: controller.prepare(
            self.bPrepare, self.bStart, self.lImage, self.lData))
        self.bStart.clicked.connect(lambda *_: controller.detectImg())
        self.rImage.clicked.connect(lambda: controller.radio_set('image'))
        self.rVidio.clicked.connect(lambda: controller.radio_set('vidio'))
        self.rCamera.clicked.connect(lambda: controller.radio_set('camera'))
        self.lImage.mousePressEvent = (lambda *_: controller.loadImg())


#运行窗口 root
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    root = Window()
    root.show()
    sys.exit(app.exec_())
