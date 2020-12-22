import random
import numpy as np
from simpleHtmlGenerator.htmlobj import HtmlObj

class Layout:

    def __init__(self,
                 parent=None,
                 width=0,
                 height=0,
                 padding_left=0,
                 padding_top=0,
                 **kwargs):
        self.parent = parent
        self._width = self.parse_expr(width, self.parent._width)
        self._height = self.parse_expr(height, self.parent._height)
        self.margin_left = 0 if self.parent == None else random.randint(0, self.parent._width - self._width)
        self.margin_top = 0 if self.parent == None else random.randint(0, self.parent._height - self._height)
        self.children_width = 0
        self.children_height = 0
        self.padding_left = self.parse_range(padding_left)
        self.padding_top = self.parse_range(padding_top)

    def parse_expr(self, expr, compare_val):
        if type(expr) is list:
            if '%' in expr[0]:
                ratio = [expr[0][:-1], expr[1][:-1]]
                val = np.multiply(ratio, compare_val)
            else:
                val = expr
            return random.randint(int(val[0]), int(val[1]))
        else:
            if '%' in expr:
                val = int(expr * compare_val)
            else:
                val = int(expr)
            return val

    def parse_range(self, listOrInt):
        if type(listOrInt) is list:
            return random.randint(listOrInt[0], listOrInt[1])
        else:
            return listOrInt

    @property
    def width(self):
        return max(self.children_width + self.padding_left, self._width)

    @property
    def height(self):
        return max(self.children_height + self.padding_top, self._height)

    def append(self, layout):
        raise NotImplementedError()

    def is_in(self):
        is_in_width = self.margin_left + self.width < self.parent._width
        in_in_height = self.margin_top + self.height < self.parent._height
        return is_in_width and in_in_height

    @property
    def layout_args(self):
        return {'width': self._width,
                'height': self._height,
                'margin-left': self.margin_left,
                'margin-top': self.margin_top,
                'padding-left': self.padding_left,
                'padding-top': self.padding_top}

    @classmethod
    def from_htmlObj(cls, htmlObj:HtmlObj):
        return Layout(htmlObj.width, htmlObj.height, padding_left=htmlObj.padding_left, padding_top=htmlObj.padding_top)

class HorizontalLayout(Layout):

    def __init__(self, child_padding, **kwargs):
        super().__init__(**kwargs)
        self.child_padding = self.parse_range(child_padding)

    def append(self, layout):
        layout.margin_left = self.child_padding
        layout.margin_top = random.randint(0, self._height - layout.height)
        self.children_width = self.children_width + layout.margin_left + layout.width

class VerticalLayout(Layout):

    def __init__(self, child_padding, **kwargs):
        super().__init__(**kwargs)
        self.child_padding = self.parse_range(child_padding)

    def append(self, layout):
        layout.margin_top = self.child_padding
        layout.margin_left = random.randint(0, self._width - layout.width)
        self.children_height = self.children_height + layout.margin_top + layout.height