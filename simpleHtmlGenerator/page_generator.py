import imgkit
import numpy as np
from simpleHtmlGenerator.htmlobj import *
from utils import io
from simpleHtmlGenerator.utils.string_utils import random_text
from simpleHtmlGenerator.layout import *

import random

def html_to_jpg(html_str, jpg_path):
    imgkit.from_string(html_str, jpg_path)

def get_expand_text_bbox(textObj):
    bbox = textObj.get_world_bbox()
    font_size = textObj.font_size

    bbox_expand = Bbox(bbox.x1 - int(font_size / 2),
                       bbox.y1 - int(font_size / 8),
                       bbox.x2 + int(font_size / 2),
                       bbox.y2 + int(font_size / 4))
    return bbox_expand

class TextGenerator:

    def __init__(self,
                 font_family,
                 font_size,
                 font_color,
                 max_char_number,
                 **kwargs):
        self.arg_font_family = font_family
        self.arg_font_size = font_size
        self.arg_font_color = font_color
        self.arg_max_char_number = max_char_number

    def random(self):
        self.font_family = random.choice(self.arg_font_family)
        self.font_size = random.randint(self.arg_font_size[0], self.arg_font_size[1])
        self.random_color()
        self.random_text()

    def random_color(self):
        self.font_color = random.choice(self.arg_font_color)

    def random_text(self):
        chars_number = random.randint(1, self.arg_max_char_number)
        self.text = random_text(chars_number)

    def __call__(self):
        textObj = TextObj(self.font_family, self.font_size, self.text, color=self.font_color)
        return textObj

class InputGenerator:

    def __init__(self,
                 input_width_range,
                 input_height_range,
                 input_board_range,
                 input_board_colors,
                 ):
        self.arg_input_width_range = input_width_range
        self.arg_input_height_range = input_height_range
        self.arg_input_board_range = input_board_range
        self.arg_input_board_colors = input_board_colors

    def random(self):
        self.width = random.randint(self.arg_input_width_range[0], self.arg_input_width_range[1])
        self.height = random.randint(self.arg_input_height_range[0], self.arg_input_height_range[1])
        self.board_size = random.randint(self.arg_input_board_range[0], self.arg_input_board_range[1])
        self.board_color = random.choice(self.arg_input_board_colors)

    def set_margin_left(self, value):
        self.margin_left = value

    def __call__(self, textGen: TextGenerator):
        width = self.width
        height = self.height
        inputObj = InputObj(width, height, self.board_size, self.board_color,
                            textGen.font_family, textGen.font_size, textGen.text, textGen.font_color)
        inputObj.margin_left = self.margin_left
        return inputObj

class VerticalGenerator:

    def __init__(self,
                 child_generator,
                 layout_args,
                 color_range,
                 **kwargs
                 ):

        self.child_generator = child_generator
        self.layout_args = layout_args
        self.color_range = color_range

    def random(self, parent_layout):
        self.child_generator.random()
        self.layout = VerticalLayout(**self.layout_args)


    def __call__(self, parent_layout):
        # call with width height limit
        background_color =
        verticalDivObj = VerticalDivObj( **self.layout.layout_args)

        while True:
            child = self.child_generator()
            child_layout = Layout.from_htmlObj(child)
            layout.append(child_layout)

            if layout.is_in(self.parent_layout):
                children_htmlObjs.append(child)




class LineTextGenerator:
    def __init__(self,
                 parent_layout,
                 text_args,
                 layout_args,
                 line_max_text,
                 line_width_percent,
                 line_height_multi_text,
                 child_padding_range,
                 **kwargs
                 ):
        self.parent_layout = parent_layout
        self.text_gen = TextGenerator(**text_args)
        self.layout_args = layout_args
        self.line_max_text = line_max_text
        self.line_width_percent = line_width_percent
        self.line_height_multi_text = line_height_multi_text
        self.child_padding_range = child_padding_range

    def random(self):
        self.text_gen.random()
        text_height = self.text_gen.arg_font_size
        width_range = np.multiply(self.parent_layout._width, self.line_width_percent)
        self.width = random.randint(width_range[0], width_range[1])
        height_range = np.multiply(text_height, self.line_height_multi_text)
        self.height = random.randint(int(height_range[0]), int(height_range[1]))
        self.child_padding = random.randint(self.child_padding_range[0], self.child_padding_range[1])
        self.random_text_number()

    def random_text_number(self):
        self.text_max_number = random.randint(1, self.line_max_text)

    def random_background_color(self):
        self.background_color = random.choice(["#ffffff", "#eeeeee", "#dddddd", "#cccccc", "#bbbbbb", "#aaaaaa"])

    def __call__(self):
        layout = HorizontalLayout(child_padding=self.child_padding, width=self.width, height=self.height, **self.layout_args)

        textObj_list = []

        for i in range(self.text_max_number):
            self.text_gen.random_text()
            self.text_gen.random_color()
            textObj = self.text_gen()
            textLayout = Layout.from_htmlObj(textObj)
            layout.append(textLayout)
            if layout.is_in(self.parent_layout):
                break
            else:
                textObj_list.append(textObj)

        divObj = DivObj(color=self.background_color, **layout.layout_args)

        for textObj in textObj_list:
            divObj.add(textObj)

        return divObj, textObj_list
#
# class InputLineGenerator:
#     def __init__(self,
#                  parent_layout,
#                  text_args,
#                  input_args,
#                  layout_args,
#                  line_width_percent,
#                  line_height_multi_text,
#                  child_padding_range,
#                  **kwargs):
#         self.parent_layout = parent_layout
#         self.layout_args = layout_args
#         self.text_gen = TextGenerator(**text_args)
#         self.input_gen = InputGenerator(**input_args)
#         self.line_width_percent = line_width_percent
#         self.arg_line_height_multi_text = line_height_multi_text
#         self.child_padding_range = child_padding_range
#
#     def random(self):
#         self.text_gen.random()
#         self.input_gen.random()
#
#         content_width = inputObj.bbox.x2
#         width = random.randint(content_width, self.arg_max_width)
#
#         content_height = max(self.text_gen.font_size, self.input_gen.height)
#         height_range = np.multiply(content_height, self.arg_line_height_multi_text)
#         height = random.randint(int(height_range[0]), int(height_range[1]))
#
#     def __call__(self, max_width):
#         textObj = self.text_gen()
#         textObj.update_bbox(0, 0)
#         anchor_x = textObj.bbox.x2
#
#         inputObj = self.input_gen(self.text_gen)
#         inputObj.update_bbox(anchor_x, 0)
#
#         content_width = inputObj.bbox.x2
#         content_height = max(textObj.bbox.y2, inputObj.bbox.y2)
#
#         margin_left_range = [0, self.arg_max_width - width]
#         margin_left = random.randint(margin_left_range[0], margin_left_range[1])
#         margin_top = random.randint(int(self.arg_line_top_margin[0]), int(self.arg_line_top_margin[1]))
#
#         padding_left_range = [0, width - content_width]
#         padding_top_range = [0, height - content_height]
#         padding_left = random.randint(padding_left_range[0], padding_left_range[1])
#         padding_top = random.randint(padding_top_range[0], padding_top_range[1])
#
#         color = random.choice(["#ffffff", "#eeeeee", "#dddddd", "#cccccc", "#bbbbbb", "#aaaaaa"])
#
#         divObj = DivObj(width - padding_left, height - padding_top, color, margin_top, margin_left, padding_top,
#                         padding_left)
#
#         divObj.add(textObj)
#         divObj.add(inputObj)
#
#         return divObj, textObj, inputObj


class TextPageGenerator:
    def __init__(self, config):
        layout = Layout(width=config['body']['width'], height=config['body']['width'])
        self.lines =
        self.lineGen = LineTextGenerator(config['text'], , **config['text_line'])
        # self.inputLineGen = InputLineGenerator(config['text'], config['input'], config['body']['width'],
        #                                        **config['input_line'])
        self.width = config['body']['width']
        self.height = config['body']['height']

    def __call__(self):
        html = PageObj(self.width, self.height)
        textObj_all = []

        anchor_y = 0
        for j in range(100):
            self.lineGen.random()
            div, textObj, _ = self.lineGen()
            div.update_bbox(0, anchor_y)
            anchor_y = div.bbox.y2

            html.add(div)
            textObj_all = textObj_all + [textObj]

            if anchor_y >= self.height:
                break

        html.update_bbox()

        bboxs = [get_expand_text_bbox(textObj) for textObj in textObj_all]
        textObj_all = [text.text for text in textObj_all]

        return html, bboxs, textObj_all


if __name__ == "__main__":
    import yaml

    with open('../conf/singleline.yaml', encoding='utf-8') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    gen = TextPageGenerator(conf)
    html, bboxs, texts = gen.gen()
    filename = "0"
    io.save_html(os.path.join("../output", "%s.html" % filename), html)
    io.save_anno(os.path.join("../output", "%s.txt" % filename), bboxs, texts)
