# -*- coding: utf-8 -*-

# 基于机器视觉的人脸表情识别系统设计-汪哲文毕业设计
#
# data.py
# 本文件为数据层，负责存储底层数据常量和模型文件
#
# 最后更新时间 2024/04/15

from enum import Enum
from cv2 import CascadeClassifier
from keras.models import load_model
from PIL import ImageFont

# 人脸识别和表情识别的模型路径
MODEL_FACE = 'models/facemodel/haarcascade_frontalface_default.xml'
MODEL_EMOTION = 'models/float_models/fer2013_mini_XCEPTION.33-0.65.hdf5'
# 载入模型数据
CLASSIFIER_FACE = CascadeClassifier(MODEL_FACE)
CLASSIFIER_EMOTION = load_model(MODEL_EMOTION, compile=False)
CLASSIFIER_EMOTION_SIZE = CLASSIFIER_EMOTION.input_shape[1:3]  # type: ignore

# 识别器的种类
RECOGNIZER_TYPE = {'image': 0, 'vidio': 1, 'camera': 2}

# 表情的标签划分
EMOTION_LABELS = {
    0: '愤怒',
    1: '厌恶',
    2: '恐惧',
    3: '快乐',
    4: '悲伤',
    5: '惊讶',
    6: '平静'
}


# 识别结果的提示词
class Result(Enum):
    PREPARE = '模型已载入'
    FINISH = '识别完成'
    CONTINUE = '检测中'
    NO_FILE_SELECTED = '未选择文件'
    LOADING = '请等待...'
    FILE_NOT_FOUND = '找不到文件'
    CAMERA_NOT_FOUND = '找不到摄像头'
    CAMERA_START = '摄像头已启动'
    FACE_NOT_FOUND = '找不到人脸'
    FACE_NOT_FOUND_CONTINUE = '检测中...'
    FACE_FOUND_SINGLE = '检测到人脸，识别结果为：'
    FACE_FOUND_MULTIPLE = '检测到 {0} 张人脸，识别结果为：\n'


# 图像路径
PATH_ORIGIN = 'temp/origin.png'
PATH_RESULT = 'temp/result.png'

# 字体路径
FONT = ImageFont.truetype('temp/msyh.ttc', 24)
