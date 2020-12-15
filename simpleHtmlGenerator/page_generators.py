import imgkit
import cv2

def html_to_jpg(html_str, jpg_path):
    imgkit.from_string(html_str, jpg_path)

class TextPageGenerator:
    def __init__(self):
