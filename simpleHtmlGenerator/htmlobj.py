import os
import sys
import uuid
import codecs
from simpleHtmlGenerator.utils.string_utils import str_count
from simpleHtmlGenerator.utils.add_px import keyforpx

class Bbox:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def __add__(self, other):
        return Bbox(self.x1 + other.x1, self.y1 + other.y1, self.x1 + other.x2, self.y1 + other.y2)

    def __str__(self):
        return "(%d, %d, %d, %d)" % (self.x1, self.y1, self.x2, self.y2)

    def make_contain(self, layout):
        """
            make self contains second layout
        """
        self.x1 = min(self.x1, layout.x1)
        self.x2 = max(self.x2, layout.x2)
        self.y1 = min(self.y1, layout.y1)
        self.y2 = max(self.y2, layout.y2)

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    @classmethod
    def from_xywh(cls, x, y, w, h):
        return Bbox(x, y, x + w, y + h)

class HtmlObj:

    def __init__(self):
        self.uuid = "a" + str(uuid.uuid4())[:8]
        self.dic = {}
        self.parent = None
        self.children = []  # will treat as child
        self._bbox = Bbox(0, 0, 0, 0)

    def add(self, child):
        self.children.append(child)
        child.parent = self

    @property
    def bbox(self):
        return self._bbox

    def update_bbox(self, start_x, start_y):
        raise NotImplementedError()

    def get_world_bbox(self, bbox=None):
        if bbox is None:
            bbox = self.bbox
        else:
            bbox = self.bbox + bbox

        if self.parent:
            bbox = self.parent.get_world_bbox(bbox)

        return bbox

    @property
    def margin_left(self):
        return self.dic['margin-left']

    @margin_left.setter
    def margin_left(self, value):
        self.dic['margin-left'] = value

    def get_css(self):
        raise NotImplementedError()

    def get_html(self):
        raise NotImplementedError()

    def destroy(self):
        if self.parent:
            self.parent = None
        if self.children:
            self.children = None

"""
    一行 有背景色
"""

class DivObj(HtmlObj):
    def __init__(self,
                 width,
                 height,
                 color,
                 margin_top,
                 margin_left,
                 padding_top,
                 padding_left,
                 **kwargs):
        super().__init__()
        self.dic['width'] = width
        self.dic['height'] = height
        self.dic['background-color'] = color
        self.dic['margin-left'] = margin_left
        self.dic['margin-top'] = margin_top
        self.dic['padding-left'] = padding_left
        self.dic['padding-top'] = padding_top

    def update_bbox(self, start_x, start_y):

        top = start_y + self.dic['margin-top']
        left = start_x + self.dic['margin-left']
        real_width = self.dic['width'] + self.dic['padding-left']
        real_height = self.dic['height'] + self.dic['padding-top']

        self._bbox = Bbox.from_xywh(left, top, real_width, real_height)

        anchor_x = self.dic['padding-left']
        anchor_y = self.dic['padding-top']

        for obj in self.children:
            obj.update_bbox(anchor_x, anchor_y)
            anchor_x = obj.bbox.x2

    def get_css(self):
        css = "div.a%s{" % self.uuid
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"

        for obj in self.children:
            css += obj.get_css()

        return css

    def get_html(self):
        html = "<div class='a%s'>\n" % self.uuid
        for obj in self.children:
            html += obj.get_html()
        html += "</div>"
        return html

    def __str__(self):
        return 'DivObj: [index: %s, layout: %s]' % (self.uuid, str(self.bbox))

"""
    几个文字
"""

class TextObj(HtmlObj):
    def __init__(self, font, size, text, color="#000000", margin_left=0):
        super().__init__()
        self.dic['font-family'] = font
        self.dic['font-size'] = size
        self.dic['color'] = color
        self.dic['margin-left'] = margin_left
        self.text = text

    def update_bbox(self, start_x, start_y):
        height = self.dic['font-size']
        num_ch, num_other = str_count(self.text)
        num = 1 * num_ch + 0.5 * num_other
        width = int(self.dic['font-size'] * num)
        self._bbox = Bbox.from_xywh(start_x+self.dic['margin-left'], start_y, width, height)

    def get_css(self):
        css = "span.a%s{" % self.uuid
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"
        return css

    def get_html(self):
        html = "<span class='a%s'>%s</span>" % (self.uuid, self.text)
        return html

    @property
    def font_size(self):
        return self.dic['font-size']

    def copy(self):
        newObj = TextObj(self.dic['font-family'], self.dic['font-size'], self.text, self.dic['color'])
        newObj.dic = self.dic.copy()
        return newObj

    def __str__(self):
        return "TextObj: " + str(self.bbox) + " " + self.text

"""
    输入框
"""

class InputObj(HtmlObj):
    def __init__(self, width, height, default_text, board_size, board_color, text_color):
        super().__init__()
        self.dic['width'] = width
        self.dic['line-height'] = height
        self.dic['border'] = "%dpx solid %s" % (board_size, board_color)

        self.default_text = default_text
        self.dic['color'] = text_color

    def update_bbox(self, start_x, start_y):
        self._bbox = Bbox.from_xywh(start_x, start_y, self.dic['width'], self.dic['line-height'])

    def get_css(self):
        css = "input.a%s{" % self.uuid
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"
        return css

    def get_html(self):
        html = "<p class='a%s' value='%s'></p>" % (self.uuid, self.default_text)
        return html


"""
    base class
"""

template = codecs.open("template.html", "r", "utf-8").read()

class PageObj(HtmlObj):
    def __init__(self, body_width, body_height):
        super().__init__()

        self.dic = {'width': body_width,
                    'height': body_height,
                    'margin-left': '0px',
                    'margin-top': '0px'}

    def add_Obj(self, obj: HtmlObj):
        self.children.append(obj)

    def update_bbox(self, start_x=0, start_y=0):
        y_anchor = 0
        for child in self.children:
            child.update_bbox(0, y_anchor)
            y_anchor = child.bbox.y2
        self._layout = Bbox.from_xywh(0, 0, self.dic['width'], y_anchor)

    def __str__(self):
        html_str = str(template)
        css_str_list = [obj.get_css() for obj in self.children]
        css_str = "".join(css_str_list)
        body_str_list = [obj.get_html() for obj in self.children]
        body_str = "".join(body_str_list)

        html_str = str.replace(html_str, "css_token", css_str)
        html_str = str.replace(html_str, "body_token", body_str)
        return html_str

if __name__ == "__main__":
    page = PageObj(1000, 1000)
    line = DivObj(300, 50, "#eeeeee", 0, 0, 10, 0)
    text = TextObj("黑体", 20, "测试123")
    text12 = TextObj("宋体", 20, "测试数字")
    line2 = DivObj(150, 30, "#ffff33", 0, 0, 0, 0)
    text2 = TextObj("宋体", 20, "测试456")
    line.add(text)
    line.add(text12)
    page.add(line)
    line2.add(text2)
    page.add(line2)
    page.update_bbox()

    text_bbox = text.get_world_bbox()
    text_bbox12 = text12.get_world_bbox()
    bbox = text2.get_world_bbox()
    from utils import io

    io.save_html(os.path.join("../output", "0.html"), page)
    io.save_anno(os.path.join("../output", "0.txt"), [text_bbox, text_bbox12, bbox], \
                 [text.text, text12.text, text2.text])
