import imgkit
import numpy as np
import cv2
import uuid
from tqdm import tqdm
import os
from pathlib import Path
from simpleHtmlGenerator.htmlobj import *
from simpleHtmlGenerator.utils.alphabets import alphabet
from simpleHtmlGenerator.utils.string_utils import str_count

import random

alphabet_arr = np.array(list(alphabet))

def html_to_jpg(html_str, jpg_path):
    imgkit.from_string(html_str, jpg_path)

def random_text(num):
    text = np.random.choice(alphabet_arr, num)
    text = "".join(text)
    return text

class RangeRandomItem():
    def __init__(self, low, up):
        self.low = low
        self.up = up

    def random(self):
        return random.randint(self.low, self.up)

class SingleLineTextGenerator:
    def __init__(self, fonts = ['宋体', '黑体', '微软雅黑'],
                 font_size_range = (30, 50),
                 chars_number = (1, 10),
                 margin_top_range = (0, 10),
                 margin_left_range = (0, 10),
                 padding_top_range = (0, 10),
                 padding_left_range = (0, 10)
                 ):
        self.fonts = fonts
        self.chars_number_item = RangeRandomItem(*chars_number)
        self.font_size_item = RangeRandomItem(*font_size_range)
        self.margin_top_item = RangeRandomItem(*margin_top_range)
        self.margin_left_item = RangeRandomItem(*margin_left_range)
        self.padding_top_item = RangeRandomItem(*padding_top_range)
        self.padding_left_item = RangeRandomItem(*padding_left_range)

    def gen(self):
        # 先得到字，再找出边缘扩张，最后左上角位移
        font_family = random.choice(self.fonts)
        font_size = self.font_size_item.random()
        chars_number = self.chars_number_item.random()
        text = random_text(chars_number)
        full, half = str_count(text)
        text_width = int(full * font_size + half * font_size / 2)

        top_margin = self.margin_top_item.random()
        left_margin = self.margin_left_item.random()

        div_width = text_width + 100
        div_height = text_width + 100
        div_color = random.choice(["#ffffff", "#eeeeee", "dddddd", "cccccc", "bbbbbb", "aaaaaa"])

        divObj = DivObj(div_width, div_height, div_color)
        divObj.set_margin(left_margin, top_margin)

        textObj = TextObj(font_family, font_size, text)
        divObj.add(textObj)

        return divObj, textObj


class TextPageGenerator:
    def __init__(self, save_path):
        self.save_path = save_path
        self.lineGen = SingleLineTextGenerator()

    def gen(self, num=10):
        for i in range(num):
            filename = str(i)
            html = PageObj(1080, 1920)
            texts = []
            for j in range(20):
                div, text = self.lineGen.gen()
                html.add(div)
                texts.append(text)

            html.update_layout()

            with open(os.path.join(self.save_path, "%s.txt" % filename), "w+") as f:
                for text in texts:
                    layout = text.get_world_layout()
                    text_str = text.text
                    f.write(str(layout.x1) + " " + str(layout.y1) + " " + str(layout.x2) + " " + str(layout.y2) + " " + str(text_str) + '\n')

            with codecs.open(os.path.join(self.save_path, "%s.html" % filename), "w", encoding='utf-8') as f:
                f.write(str(html))

if __name__ == "__main__":
    gen = TextPageGenerator("../output")
    gen.gen()


