import os
import sys
import uuid
import codecs
from simpleHtmlGenerator.utils import string_utils
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

    def __init__(self,
                 width=0,
                 height=0,
                 margin_left=0,
                 margin_top=0,
                 padding_left=0,
                 padding_top=0,
                 **kwargs
                 ):
        self.uuid = "a" + str(uuid.uuid4())[:8]
        self.dic = {'width':width, 'height':height, 'padding-left':padding_left,
                    'padding-top':padding_top, 'margin-left':margin_left, 'margin-top':margin_top}
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
        self._bbox = Bbox.from_xywh(start_x + self.dic['margin-left'], start_y+self.dic['margin-top'],
                          self.dic['padding-left'] + self.dic['width'], self.dic['padding-top'] + self.dic['height'])

    def get_world_bbox(self, bbox=None):
        if bbox is None:
            bbox = self.bbox
        else:
            bbox = self.bbox + bbox

        if self.parent:
            bbox = self.parent.get_world_bbox(bbox)

        return bbox

    @property
    def width(self):
        return self.dic['padding-left'] + self.dic['width']

    @property
    def height(self):
        return self.dic['padding-top'] + self.dic['height']

    def get_css(self):
        raise NotImplementedError()

    def get_html(self):
        raise NotImplementedError()

    def destroy(self):
        if self.parent:
            self.parent = None
        if self.children:
            self.children = None

    def get_text_world_bbox(self):
        return self.get_world_bbox()

class ContainerObj(HtmlObj):
    def __init__(self,
                 background_color = "#ffffff",
                 **kwargs
                 ):
        super(ContainerObj, self).__init__(**kwargs)
        self.dic['background-color'] = background_color

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

class VerticalDivObj(ContainerObj):

    def update_bbox(self, start_x, start_y):

        super().update_bbox(start_x, start_y)

        anchor_x = self.dic['padding-left']
        anchor_y = self.dic['padding-top']

        for obj in self.children:
            obj.update_bbox(anchor_x, anchor_y)
            anchor_y = obj.bbox.y2

class HorizontalDivObj(ContainerObj):

    def update_bbox(self, start_x, start_y):

        super().update_bbox(start_x, start_y)

        anchor_x = self.dic['padding-left']
        anchor_y = self.dic['padding-top']

        for obj in self.children:
            obj.update_bbox(anchor_x, anchor_y)
            anchor_x = obj.bbox.x2

"""
    几个文字
"""

class TextObj(HtmlObj):
    def __init__(self, font, size, text, color="#000000", **kwargs):
        super().__init__(**kwargs)
        self.dic['font-family'] = font
        self.dic['font-size'] = size
        self.dic['color'] = color
        self.text = text

    def update_bbox(self, start_x, start_y):
        self.dic['height'] = self.dic['font-size']
        self.dic['width'] = string_utils.get_text_width(self.text, self.dic['font-size'])
        super().update_bbox(start_x, start_y)

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

    def __str__(self):
        return "TextObj: " + str(self.bbox) + " " + self.text

"""
    输入框
"""

class InputObj(HtmlObj):
    def __init__(self, font_family, font_size, default_text, board_size, board_color, text_color, **kwargs):
        super().__init__(**kwargs)
        self.dic['border'] = "%dpx solid %s" % (board_size, board_color)
        self.dic['font-family'] = font_family
        self.dic['font-size'] = font_size
        self.text = default_text
        self.dic['color'] = text_color

    def get_css(self):
        css = "input.a%s{" % self.uuid
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"
        return css
    
    def update_bbox(self, start_x, start_y):
        width = max(self.dic['width'], string_utils.get_text_width(self.text, self.dic['font-size']))
        height = max(self.dic['height'], self.dic['font-size'])
        self.dic['width'] = width
        self.dic['height'] = height
        super(InputObj, self).update_bbox(start_x, start_y)

    def get_html(self):
        html = "<input class='a%s' value='%s'></p>" % (self.uuid, self.text)
        return html

    def get_text_world_bbox(self):
        height = self.dic['font-size']
        width = string_utils.get_text_width(self.text, self.dic['font-size'])
        bbox = Bbox.from_xywh(self.dic['margin-left'], self.dic['margin-top'], width, height)
        world_bbox = self.get_world_bbox(bbox)
        return world_bbox
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
        for child in self.children:
            child.update_bbox(0, 0)
        self._bbox = Bbox.from_xywh(0, 0, self.dic['width'], self.dic['height'])

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
    page = PageObj(500, 500)
    v_con = VerticalDivObj(width=500, height=500)
    page.add(v_con)
    line = HorizontalDivObj(background_color="#eeeeee", width=300, height=50, padding_left=10)
    text = TextObj("黑体", 20, "测试123")
    input = InputObj("宋体", 20, "输入内容", 1, board_color="#666666", text_color="#ff0000", height=20)
    line2 = HorizontalDivObj(background_color="#ffff33", width=150, height=30)
    text2 = TextObj("宋体", 20, "测试456")
    line.add(text)
    line.add(input)
    v_con.add(line)
    line2.add(text2)
    v_con.add(line2)

    page.update_bbox()

    text_bbox = text.get_text_world_bbox()
    text_bbox12 = input.get_text_world_bbox()
    bbox = text2.get_text_world_bbox()
    from utils import io

    io.save_html(os.path.join("../output", "0.html"), page)
    io.save_anno(os.path.join("../output", "0.txt"), [text_bbox, text_bbox12, bbox], \
                 [text.text, input.text, text2.text])
