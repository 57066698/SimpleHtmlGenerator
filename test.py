import imgkit
import cv2

imgkit.from_file("result.html", "1.jpg")

img = cv2.imread("1.jpg")

img = cv2.rectangle(img, (-15, 0), (135, 30), (255, 0, 0), 1)
cv2.imwrite("1.jpg", img)