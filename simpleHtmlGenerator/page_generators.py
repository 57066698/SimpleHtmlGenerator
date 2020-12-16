import imgkit
import cv2
from tqdm import tqdm
from pathlib import Path
from simpleHtmlGenerator.htmlobj import *
import random

def html_to_jpg(html_str, jpg_path):
    imgkit.from_string(html_str, jpg_path)

class SimgleLineTextGenerator:
    def __init__(self, fonts = ['宋体', '黑体', '微软雅黑'],
                 font_size_range = [30, 50],
                 top_margin_range = [0, 10],
                 left_margin_range = [0, 10],
                 top_padding_range = [0, 10],
                 left_padding_range = [0, 10]
                 ):
        self.fonts = fonts
        self.font_size_range = font_size_range
        self.top_margin_range = top_margin_range
        self.left_margin_range = left_margin_range
        self.top_padding_range = top_padding_range
        self.left_margin_range = left_padding_range

    def get(self):
        font_family = random.choice(self.fonts)
        font_size = random.randint(self.font_size_range[0], self.font_size_range[1])


class TextPageGenerator:
    def __init__(self, save_path, fonts, font_size_range):
        self.save_path = save_path


