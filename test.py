import imgkit
import cv2

imgkit.from_file("output/0.html", "1.jpg")

img = cv2.imread("1.jpg")

with open("output/0.txt", "r") as f:
    lines = f.read().split('\n')
    for i in range(len(lines)-1):
        x1, y1, x2, y2, text = lines[i].split(" ")
        img = cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 1)

cv2.imwrite("1.jpg", img)