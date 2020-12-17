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

class TextGenerator:
    def __init__(self,
                 font_family,
                 max_char_number,
                 font_size,
                 font_color,
                 **kwargs
                 ):
        self.font_family = font_family
        self.max_char_number = max_char_number
        self.font_size = font_size
        self.font_color = font_color

    def gen(self):
        font = random.choice(self.font_family)
        font_size = random.randint(self.font_size[0], self.font_size[1])
        chars_number = random.randint(1, self.max_char_number)
        text = random_text(chars_number)

        textObj = TextObj(font, font_size, text)
        textObj.update_layout(0, 0)

        return textObj

class SingleLineTextGenerator:
    def __init__(self,
                 text_args,
                 body_width,
                 line_width_percent,
                 line_height_multi_text,
                 line_left_margin_percent,
                 line_top_margin,
                 line_padding,
                 **kwargs
                 ):
        self.text_gen = TextGenerator(**text_args)
        self.body_width = body_width
        self.line_width_percent = line_width_percent
        self.line_left_margin_percent = line_left_margin_percent
        self.line_padding = line_padding
        self.line_height_multi_text = line_height_multi_text
        self.line_top_margin = line_top_margin

    def gen(self):
        # 先得到字
        textObj = self.text_gen.gen()
        text_w, text_h = textObj.layout.width, textObj.layout.height

        # 得到宽度
        width_range = np.multiply(self.body_width, self.line_width_percent)
        width_range = np.clip(width_range, text_w, self.body_width)
        width = random.randint(int(width_range[0]), int(width_range[1]))

        # 得到高度
        height_range = np.multiply(text_h, self.line_height_multi_text)
        height = random.randint(int(height_range[0]), int(height_range[1]))

        # 得到margin
        margin_left_range = [0, self.body_width - width]
        margin_left = random.randint(margin_left_range[0], margin_left_range[1])
        margin_top = random.randint(int(self.line_top_margin[0]), int(self.line_top_margin[1]))

        # 得到padding
        padding_left_range = [0, width - text_w]
        padding_top_range = [0, height - text_h]
        padding_left = random.randint(padding_left_range[0], padding_left_range[1])
        padding_top = random.randint(padding_top_range[0], padding_top_range[1])

        color = random.choice(["#ffffff", "#eeeeee", "dddddd", "cccccc", "bbbbbb", "aaaaaa"])

        divObj = DivObj(width, height, color, margin_top, margin_left, padding_top, padding_left)
        divObj.add(textObj)

        return divObj, textObj

class TextPageGenerator:
    def __init__(self, save_path, config):
        self.save_path = save_path
        self.lineGen = SingleLineTextGenerator(config['text'], config['body']['width'], **config['line'])
        self.width = config['body']['width']
        self.height = config['body']['height']

    def gen(self, num=1):
        for i in range(num):
            filename = str(i)
            html = PageObj(self.width, self.height)
            texts = []
            for j in range(10):
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

    import yaml
    with open('../conf/singleline.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    gen = TextPageGenerator("../output", conf)
    gen.gen()