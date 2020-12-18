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
    一个块 有背景色
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

    @property
    def text_item(self):
        return None if len(self.children) == 0 else self.children[0]

    def update_bbox(self, start_x, start_y):

        top = start_y + self.dic['margin-top']
        left = start_x + self.dic['margin-left']
        real_width = self.dic['width'] + self.dic['padding-left']
        real_height = self.dic['height'] + self.dic['padding-top']

        self._bbox = Bbox.from_xywh(left, top, real_width, real_height)

        if len(self.children) > 0:
            textObj = self.children[0]
            padding_top = 0 if 'padding-top' not in self.dic else self.dic['padding-top']
            padding_left = 0 if 'padding-left' not in self.dic else self.dic['padding-left']
            textObj.update_bbox(padding_left, padding_top)
            # text_layout = textObj.layout
            #todo: self.layout.make_contain(text_layout)

    def get_css(self):
        css = "div.a%s{" % self.uuid
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"

        if not self.children is None:
            css += self.text_item.get_css()

        return css

    def get_html(self):
        if not self.children is None:
            text_heml = self.text_item.get_html()
            html = "<div class='a%s'>%s</div>\n" % (self.uuid, text_heml)
        else:
            html = "<div class='a%d'></div>\n"
        return html

    def __str__(self):
        return 'DivObj: [index: %s, layout: %s]' % (self.uuid, str(self.bbox))


"""
    一行文字
"""


class TextObj(HtmlObj):
    def __init__(self, font, size, text, color="#000000"):
        super().__init__()
        self.dic['font-family'] = font
        self.dic['font-size'] = size
        self.dic['color'] = color
        self.text = text

    def update_bbox(self, start_x, start_y):
        self._bbox = Bbox.from_xywh(start_x, start_y, self.width, self.height)

    @property
    def height(self):
        return self.dic['font-size']

    @property
    def width(self):
        num_ch, num_other = str_count(self.text)
        num = 1 * num_ch + 0.5 * num_other
        return int(self.dic['font-size'] * num)

    def get_css(self):
        css = "p.a%s{" % self.uuid
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"
        return css

    def get_html(self):
        html = "<p class='a%s'>%s</p>" % (self.uuid, self.text)
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
    page = PageObj(200, 200)
    line = DivObj(120, 50, "#eeeeee", 0, 0, 10, 0)
    text = TextObj("黑体", 20, "测试123")
    line2 = DivObj(150, 30, "#ffff33", 0, 0, 0, 0)
    text2 = TextObj("宋体", 20, "测试456")
    line.add(text)
    page.add(line)
    line2.add(text2)
    page.add(line2)
    page.update_bbox()

    text_bbox = text.get_world_bbox()
    bbox = text2.get_world_bbox()
    from utils import io

    io.save_html(os.path.join("../output", "0.html"), page)
    io.save_anno(os.path.join("../output", "0.txt"), [text_bbox, bbox], \
                 [text.text, text2.text])
