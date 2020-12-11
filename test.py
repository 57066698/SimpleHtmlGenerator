import imgkit
import cv2

imgkit.from_file("1.html", "1.jpg")

img = cv2.imread("1.jpg")
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img = cv2.rectangle(img, (100, 0), (100+15*4, 15), (255, 0, 0), 1)
cv2.imwrite("1.jpg", img)