import os
import sys
import codecs
from simpleHtmlGenerator.utils.string_count import str_count
from simpleHtmlGenerator.utils.add_px import keyforpx

class Layout:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def __add__(self, other):
        return Layout(self.x1+other.x1, self.y1+other.y1, self.x1+other.x2, self.y1+other.y2)

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

    @classmethod
    def from_xywh(cls, x, y, w, h):
        return Layout(x, y, x+w, y+h)



class HtmlObj:

    def __init__(self):
        self.dic = {}
        self.parent = None
        self.children = []  # will treat as child
        self._layout = Layout(0, 0, 0, 0)

    def add(self, child):
        self.children.append(child)
        child.parent = self

    @property
    def layout(self):
        return self._layout

    def update_layout(self, start_x, start_y):
        raise NotImplementedError()

    def get_world_layout(self, layout=None):
        if layout is None:
            layout = self.layout
        else:
            layout = self.layout + layout

        if self.parent:
            layout = self.parent.get_world_layout(layout)

        return layout

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
    一个块 有背景色 内含一个text
"""

class DivObj(HtmlObj):
    def __init__(self, index, width, height, color):
        super().__init__()
        self.dic['width'] = width
        self.dic['height'] = height
        self.dic['background-color'] = color
        self.index = index

    @property
    def text_item(self):
        return None if len(self.children) == 0 else self.children[0]

    def set_padding(self, left, top):
        """
            内边界
        """
        self.dic['padding-left'] = int(left)
        self.dic['padding-top'] = int(top)

    def set_margin(self, left, top):
        """
            外边界
        """
        self.dic['margin-left'] = int(left)
        self.dic['margin-top'] = int(top)

    def update_layout(self, start_x, start_y):
        top = start_y
        if 'margin-top' in self.dic:
            top = top + self.dic['margin-top']
        left = start_x
        if 'margin-left' in self.dic:
            left = left + self.dic['margin-left']

        self._layout = Layout.from_xywh(left, top, self.dic['width'], self.dic['height'])

        if len(self.children) > 0:
            textObj = self.children[0]
            padding_top = 0 if 'padding-top' not in self.dic else self.dic['padding-top']
            padding_left = 0 if 'padding-left' not in self.dic else self.dic['padding-left']
            textObj.update_layout(padding_left, padding_top)
            # text_layout = textObj.layout
            #todo: self.layout.make_contain(text_layout)

    def get_css(self):
        css = "div.a%d{" % self.index
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
            html = "<div class='a%d'>%s</div>\n" % (self.index, text_heml)
        else:
            html = "<div class='a%d'></div>\n"
        return html

    def __str__(self):
        return 'DivObj: [index: %d, layout: %s]' % (self.index, str(self.layout))


"""
    一行文字
"""


class TextObj(HtmlObj):
    def __init__(self, index, font, size, text, color="#000000"):
        super().__init__()
        self.dic['font-family'] = font
        self.dic['font-size'] = size
        self.dic['color'] = color
        self.index = index
        self.text = text

    def update_layout(self, start_x, start_y):
        self._layout = Layout.from_xywh(start_x, start_y, self.width, self.height)

    @property
    def height(self):
        return self.dic['font-size']

    @property
    def width(self):
        num_ch, num_other = str_count(self.text)
        num = 1 * num_ch + 0.5 * num_other
        return int(self.dic['font-size'] * num)

    def get_css(self):
        css = "p.a%d{" % self.index
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"
        return css

    def get_html(self):
        html = "<p class='a%d'>%s</p>" % (self.index, self.text)
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

    def update_layout(self, start_x=0, start_y=0):
        y_anchor = 0
        for child in self.children:
            child.update_layout(0, y_anchor)
            y_anchor = child.layout.y2
        self._layout = Layout.from_xywh(0, 0, self.dic['width'], y_anchor)

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
    print("test....")
    html = PageObj(1080, 1920)

    divObj1 = DivObj(1, width=400, height=50, color='#aaaa55')
    textObj1 = TextObj(1, size=30, font="微软雅黑", text="测试中文", color="#ff0000")
    divObj1.add(textObj1)
    html.add_Obj(divObj1)

    divObj2 = DivObj(2, width=200, height=50, color='#aa55aa')
    textObj2 = TextObj(2, size=30, font="仿宋_GB2312", text="测试中文", color="#0000ff")
    divObj2.set_margin(100, 20)
    divObj2.set_padding(100, 20)
    divObj2.add(textObj2)
    html.add_Obj(divObj2)

    html.update_layout()

    print(textObj1.get_world_layout())
    print(textObj2.get_world_layout())
    with codecs.open("../result.html", "w", encoding='utf-8') as f:
        f.write(str(html))
