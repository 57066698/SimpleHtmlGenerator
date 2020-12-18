import imgkit
import numpy as np
from simpleHtmlGenerator.htmlobj import *
from utils import io
from simpleHtmlGenerator.utils.string_utils import random_text

import random



def html_to_jpg(html_str, jpg_path):
    imgkit.from_string(html_str, jpg_path)

def get_expand_text_bbox(textObj):

    bbox = textObj.get_world_bbox()
    font_size = textObj.font_size

    bbox_expand = Bbox(bbox.x1 - int(font_size/2),
                bbox.y1 - int(font_size/8),
                bbox.x2 + int(font_size/2),
                bbox.y2 + int(font_size/4))
    return bbox_expand

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
        textObj.update_bbox(0, 0)
        return textObj

    def gen_with_copy(self, textObj):
        chars_number = random.randint(1, self.max_char_number)
        text = random_text(chars_number)
        newObj = textObj.copy()
        newObj.text = text
        return newObj

class InputGenerator:
    def __init__(self,
                 input_max_width,
                 input_height_range,
                 input_margin_left_range,
                 ):
        self.input_max_width = input_max_width
        self.input_height_range = input_height_range
        self.input_margin_left_range = input_margin_left_range

    def gen(self):
        width = random.randint(self.input_max_width[0], self.input_max_width[1])

class LineTextGenerator:
    def __init__(self,
                 text_args,
                 max_width,
                 line_max_text,
                 line_text_gap_range,
                 line_width_percent,
                 line_height_multi_text,
                 line_left_margin_percent,
                 line_top_margin,
                 line_padding,
                 **kwargs
                 ):
        self.text_gen = TextGenerator(**text_args)
        self.max_width = max_width
        self.line_max_text = line_max_text
        self.line_text_gap_range = line_text_gap_range
        self.line_width_percent = line_width_percent
        self.line_left_margin_percent = line_left_margin_percent
        self.line_padding = line_padding
        self.line_height_multi_text = line_height_multi_text
        self.line_top_margin = line_top_margin

    def _gen_texts(self, max_width):

        text_max_number = random.randint(1, self.line_max_text)
        line_text_gap = random.randint(self.line_text_gap_range[0], self.line_text_gap_range[1])

        anchor_x = 0
        textObj_template = None

        textObj_list = []

        while anchor_x <= max_width and len(textObj_list) < text_max_number:
            if textObj_template is None:
                textObj = textObj_template = self.text_gen.gen()
            else:
                textObj = self.text_gen.gen_with_copy(textObj_template)
                textObj.margin_left = line_text_gap
            textObj.update_bbox(anchor_x, 0)

            if textObj.bbox.x2 <= max_width:
                anchor_x = textObj.bbox.x2
                textObj_list.append(textObj)
            else:
                break

            anchor_x = anchor_x + line_text_gap

        total_width = anchor_x - line_text_gap
        return textObj_list, total_width, textObj_template.bbox.y2

    def gen(self):

        # 得到字
        textObj_list, total_width, text_height = self._gen_texts(self.max_width)

        # 得到宽度
        width_range = np.multiply(self.max_width, self.line_width_percent)
        width_range = np.clip(width_range, total_width, self.max_width)
        width = random.randint(int(width_range[0]), int(width_range[1]))

        # 得到高度
        height_range = np.multiply(text_height, self.line_height_multi_text)
        height = random.randint(int(height_range[0]), int(height_range[1]))

        # 得到margin
        margin_left_range = [0, self.max_width - width]
        margin_left = random.randint(margin_left_range[0], margin_left_range[1])
        margin_top = random.randint(int(self.line_top_margin[0]), int(self.line_top_margin[1]))

        # 得到padding
        padding_left_range = [0, width - total_width]
        padding_top_range = [0, height - text_height]
        padding_left = random.randint(padding_left_range[0], padding_left_range[1])
        padding_top = random.randint(padding_top_range[0], padding_top_range[1])

        color = random.choice(["#ffffff", "#eeeeee", "#dddddd", "#cccccc", "#bbbbbb", "#aaaaaa"])

        divObj = DivObj(width - padding_left, height - padding_top, color, margin_top, margin_left, padding_top,
                        padding_left)

        for textObj in textObj_list:
            divObj.add(textObj)

        return divObj, textObj_list

class InputTextGenerator:
    def __init__(self,
                 text_args,
                 input_max_width,
                 input_margin_left_range,
                 line_height_multi_text,
                 line_left_margin_percent,
                 line_top_margin,
                 line_padding):
        self.text_gen = text_args
        self.input_max_width = input_max_width
        self.input_margin_left_range = input_margin_left_range
        self.line_height_multi_text = line_height_multi_text
        self.line_left_margin_percent = line_left_margin_percent
        self.line_top_margin = line_top_margin
        self.line_padding = line_padding

    def gen(self):

        textObj = self.text_gen.gen()
        textObj.update_bbox(0, 0)
        anchor_x = textObj.bbox.x2

        inputObj
        anchor_x += random.randint(self.input_margin_left_range[0], self.input_margin_left_range[1])



class TextPageGenerator:
    def __init__(self, config):
        self.lineGen = LineTextGenerator(config['text'], config['body']['width'], **config['text_line'])
        self.width = config['body']['width']
        self.height = config['body']['height']

    def gen(self):
        html = PageObj(self.width, self.height)
        textObj_all = []

        anchor_y = 0
        for j in range(100):
            div, textObj_list = self.lineGen.gen()
            div.update_bbox(0, anchor_y)
            anchor_y = div.bbox.y2

            html.add(div)
            textObj_all = textObj_all + textObj_list

            if anchor_y >= self.height:
                break

        html.update_bbox()

        bboxs = [get_expand_text_bbox(textObj) for textObj in textObj_all]
        textObj_all = [text.text for text in textObj_all]

        return html, bboxs, textObj_all

if __name__ == "__main__":

    import yaml
    with open('../conf/singleline.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    gen = TextPageGenerator(conf)
    html, bboxs, texts = gen.gen()
    filename = "0"
    io.save_html(os.path.join("../output", "%s.html" % filename), html)
    io.save_anno(os.path.join("../output", "%s.txt" % filename), bboxs, texts)