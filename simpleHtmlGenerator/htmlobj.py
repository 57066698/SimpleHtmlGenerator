import os
import sys
import codecs
from simpleHtmlGenerator.utils.string_count import str_count

class HtmlObj:

    def __init__(self):
        self.dic = {}
        self.parent = None
        self.children = None # will treat as child

    def add(self, child):
        self.children = child
        child.parent = self

    def get_world_bbox(self, bbox=None):
        if bbox is None:
            try:
                bbox = self.bbox
            except:
                return None
        if self.parent:
            bbox = self.parent.get_world_bbox(bbox)

        left, top = 0, 0
        if 'margin-top' in self.dic:
            top += self.dic['margin-top']
        if 'padding-top' in self.dic:
            top += self.dic['padding-top']
        if 'margin-left' in self.dic:
            left += self.dic['margin-left']
        if 'padding-left' in self.dic:
            left += self.dic['padding-left']
        bbox = (bbox[0]+left, bbox[1]+top, bbox[2]+left, bbox[3]+top)
        return bbox

    def get_css(self):
        raise NotImplementedError()

    def get_html(self):
        raise NotImplementedError()

    @property
    def height(self):
        raise NotImplementedError()

    @property
    def bbox(self):
        raise NotImplementedError()

    def destroy(self):
        if self.parent:
            self.parent = None
        if self.children:
            self.children = None

def keyforpx(key, val):
    val = str(val)
    if 'size' in key or 'margin' in key or 'padding' in key or 'width' in key or 'height' in key:
        val = str(val) + 'px'
    return val

"""
    一个块 有背景色 内含一个text
"""

class DivHtmlObj(HtmlObj):
    def __init__(self, index, width, height, color):
        super().__init__()
        self.dic['width'] = width
        self.dic['height'] = height
        self.dic['background-color'] = color
        self.index = index

    def add(self, text):
        super().add(text)
        if text.height > self.dic['height']:
            self.dic['height'] = text.height

    def set_padding(self, left, top):
        """
            内边界
        :param left:
        :param top:
        :return:
        """
        self.dic['padding-left'] = int(left)
        self.dic['padding-top'] = int(top)

    def set_margin(self, left, top):
        """
            外边界
        :param left:
        :param top:
        :return:
        """
        self.dic['margin-left'] = int(left)
        self.dic['margin-top'] = int(top)

    @property
    def height(self):
        if 'margin-left' in self.dic:
            return self.dic['height'] + self.dic['margin-left']
        return self.dic['height']

    def get_css(self):
        css = "div.a%d{" % self.index
        for key in self.dic:
            css += str(key)
            css += ": "
            css += keyforpx(key, self.dic[key])
            css += "; "
        css += "}\n"

        if not self.children is None:
            css += self.children.get_css()

        return css

    def get_html(self):
        if not self.children is None:
            text_heml = self.children.get_html()
            html = "<div class='a%d'>%s</div>\n" % (self.index, text_heml)
        else:
            html = "<div class='a%d'></div>\n"
        return html

"""
    一行文字
"""

class TextHtmlObj(HtmlObj):
    def __init__(self, index, font, size, text, color="#000000"):
        super().__init__()
        self.dic['font'] = font
        self.dic['font-size'] = size
        self.dic['color'] = color
        self.index = index
        self.text = text

    @property
    def height(self):
        return self.dic['font-size']

    @property
    def width(self):
        num_ch, num_other = str_count(self.text)
        num = 1 * num_ch + 0.5 * num_other
        return int(self.dic['font-size'] * num)

    @property
    def bbox(self):
        expand = int(self.dic['font-size'] / 2)
        return (-expand, 0, self.width+expand, self.height)

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

class HTML:
    def __init__(self, body_width, body_height):
        self.dic = {'width':body_width,
                    'height':body_height,
                    'margin-left':'0px',
                    'margin-top':'0px'}
        self.objs = []

    def add_Obj(self, obj:HtmlObj):
        self.objs.append(obj)

    @property
    def height(self):
        height = [obj.height for obj in self.objs]
        height = sum(height)
        return height

    def __str__(self):
        html_str = str(template)
        css_str_list = [obj.get_css() for obj in self.objs]
        css_str = "".join(css_str_list)
        body_str_list = [obj.get_html() for obj in self.objs]
        body_str = "".join(body_str_list)

        html_str = str.replace(html_str, "css_token", css_str)
        html_str = str.replace(html_str, "body_token", body_str)
        return html_str

if __name__ == "__main__":
    print("test....")
    divObj1 = DivHtmlObj(1, width=400, height=50, color='#aaaa55')
    # divObj1.set_padding(100, 10)
    textObj1 = TextHtmlObj(1, size=30, font="黑体", text="测试中文", color="#ff0000")
    divObj2 = DivHtmlObj(2, width=200, height=100, color='#aa55aa')
    textObj2 = TextHtmlObj(2, size=30, font="黑体", text="测试测试测试", color="#0000ff")
    divObj2.set_padding(100, 20)
    divObj1.add(textObj1)
    divObj2.add(textObj2)
    html = HTML(1080, 1920)
    html.add_Obj(divObj1)
    html.add_Obj(divObj2)
    print(textObj1.get_world_bbox())
    with codecs.open("../result.html", "w", encoding='utf-8') as f:
        f.write(str(html))


