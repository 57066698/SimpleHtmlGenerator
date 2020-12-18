import imgkit
import cv2
from utils import io

imgkit.from_file("output/0.html", "1.jpg")
# imgkit.from_file('1.html', '1.jpg')

img = cv2.imread("1.jpg")

bboxs, texts = io.load_anno("output/0.txt")

for i in range(len(bboxs)):
    x1, y1, x2, y2 = bboxs[i]
    img = cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 1)

cv2.imwrite("1.jpg", img)