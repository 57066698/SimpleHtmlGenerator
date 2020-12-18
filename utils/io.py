import os
import codecs

def save_html(path, html_str):
    with codecs.open(path, "w+", encoding='utf-8') as f:
        f.write(str(html_str))

def save_anno(path, layouts, texts):

    with open(path, "w+") as f:
        for i in range(len(layouts)):
            layout = layouts[i]
            text = texts[i]
            f.write(str(layout.x1) + " " + str(layout.y1) + " " + str(layout.x2) + " "\
                    + str(layout.y2) + " " + str(text) + '\n')

def load_anno(path):

    bboxs = []
    texts = []

    with open(path, "r") as f:
        lines = f.read().split('\n')
        for i in range(len(lines) - 1):
            x1, y1, x2, y2, text = lines[i].split(" ")
            bboxs.append([int(x1), int(y1), int(x2), int(y2)])
            texts.append(text)

    return bboxs, texts