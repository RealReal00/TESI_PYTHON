import cv2
from aaa_classi import YOLO_Pred



yolo = YOLO_Pred('./data/best.onnx','./data.yaml')

#img = cv2.imread('./img_2.jpg')

#yolo.apply_tesseract('.\data\img_2.jpg',)
# predictions

_, output = yolo.predictions('.\data\img_2.jpg')
print('______________________________________')
print(output)




