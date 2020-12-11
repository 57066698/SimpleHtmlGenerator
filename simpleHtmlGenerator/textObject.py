idx = 0

class textBlock:
    def __init__(self, font, size, text, color="black"):

        self.dic = {'font': font,
                    'font-size': size,
                    'color': color}

        global idx
        self.idx = idx
        idx = idx + 1

    @classmethod
    def


    @property
    def css(self):
        font = "font:%s" % self.font
        size = "font-size:%s" % self.size
        color = "color:%" % self.color

        padding = ""

        for arg in ['left_padding, right_padding, left_margin, right_margin']:
            if self[arg] != 0:


        return "p.%d {%s;%s;%s;%s}" % (self.idx, font, size, color, )

print(textBlock(0, 0, 0).css)