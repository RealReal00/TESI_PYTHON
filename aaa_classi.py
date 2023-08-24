import self as self
from PIL import Image, ImageTk
import pytesseract

import cv2
import numpy as np
import os
import yaml
from yaml.loader import SafeLoader
import tkinter as tk
from tkinter import ttk

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class YOLO_Pred():
    def __init__(self, onnx_model, data_yaml):

        # load YAML
        with open('./data/data.yaml', mode='r') as f:
            data_yaml = yaml.load(f, Loader=SafeLoader)

        self.labels = data_yaml['names']


        # load YOLO model
        self.yolo = cv2.dnn.readNetFromONNX('./data/best.onnx')
        self.yolo.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.yolo.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        #self.predictions("./data/img_2.jpg")


    def apply_tesseract(self, image, boxes_np, classes, index):
        vett = []

        for ind in index:
            x, y, w, h = boxes_np[ind]
            class_name = self.labels[classes[ind]]

            if class_name != "image":
                roi = image[y:y + h, x:x + w]

                ocr_text = pytesseract.image_to_string(roi)

                vett.append(ocr_text + '\n')
                print(ocr_text)

        output = '\n'.join(vett)

        return output


    def predictions(self, image):
        # load the image
        img = cv2.imread(image)
        image = img.copy()
        row, col, d = image.shape


        # get the YOLO prediction from the image
        # step-1 convert image into square image (array)
        max_rc = max(row,col)
        input_image = np.zeros((max_rc,max_rc,3),dtype=np.uint8)
        input_image[0:row,0:col] = image
        # step-2: get prediction from square array
        INPUT_WH_YOLO = 1280
        blob = cv2.dnn.blobFromImage(input_image,1/255,(INPUT_WH_YOLO,INPUT_WH_YOLO),swapRB=True,crop=False)
        self.yolo.setInput(blob)
        preds = self.yolo.forward() # detection or prediction from YOLO

        print(preds.shape)

        # Non Maximum Supression
        # step-1: filter detection based on confidence (0.4) and probability score (0.25)
        detections = preds[0]
        boxes = []
        confidences = []
        classes = []

        # widht and height of the image (input_image)
        image_w, image_h = input_image.shape[:2]
        x_factor = image_w / INPUT_WH_YOLO
        y_factor = image_h / INPUT_WH_YOLO

        for i in range(len(detections)):
            row = detections[i]
            confidence = row[4]  # confidence of detection an object
            if confidence > 0.4:
                class_score = row[5:].max()  # maximum probability from 20 objects
                class_id = row[5:].argmax()  # get the index position at which max probabilty occur

                if class_score > 0.25:
                    cx, cy, w, h = row[0:4]
                    # construct bounding from four values
                    # left, top, width and height
                    left = int((cx - 0.5 * w) * x_factor)
                    top = int((cy - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)

                    box = np.array([left, top, width, height])

                    # append values into the list
                    confidences.append(confidence)
                    boxes.append(box)
                    classes.append(class_id)

        # clean
        boxes_np = np.array(boxes).tolist()
        confidences_np = np.array(confidences).tolist()

        # NMS
        index = cv2.dnn.NMSBoxes(boxes_np, confidences_np, 0.25, 0.45).flatten()
        draw_image = image.copy()
        # Draw the Bounding
        for ind in index:
            # extract bounding box
            x, y, w, h = boxes_np[ind]
            bb_conf = int(confidences_np[ind] * 100)
            classes_id = classes[ind]
            class_name = self.labels[classes_id]
            if class_name != "image":
                # Aumento delle dimensioni del rettangolo del 10%
                w_new = int(w * 1.1)
                h_new = int(h * 1.1)
                x_new = x - int((w_new - w) / 2)
                y_new = y - int((h_new - h) / 2)

                # Applica il clipping delle coordinate per rimanere all'interno dell'immagine
                x_new = max(x_new, 0)
                y_new = max(y_new, 0)
                x_new = min(x_new, draw_image.shape[1] - w_new)
                y_new = min(y_new, draw_image.shape[0] - h_new)

                text = f'{class_name}: {bb_conf}%'

                cv2.rectangle(draw_image, (x_new, y_new), (x_new + w_new, y_new + h_new), (0, 255, 0), 2)
                cv2.rectangle(draw_image, (x_new, y_new - 30), (x_new + w_new, y_new), (255, 255, 255), -1)
                cv2.putText(draw_image, text, (x_new, y_new - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 0), 1)



        # Creazione di una finestra Tkinter per visualizzare l'immagine scorribile
        scrollable_window = tk.Tk()
        scrollable_window.title("Scrollable Image")

        # Creazione di uno scorrevole Frame
        canvas = tk.Canvas(scrollable_window, scrollregion=(0, 0, image.shape[1], image.shape[0]))
        hscroll = ttk.Scrollbar(scrollable_window, orient="horizontal", command=canvas.xview)
        vscroll = ttk.Scrollbar(scrollable_window, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # Carica l'immagine da opencv a PIL
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_tk = ImageTk.PhotoImage(image_pil)

        # Visualizza l'immagine nel Frame
        canvas.create_image(0, 0, anchor="nw", image=image_tk)

        scrollable_window.mainloop()
        output = self.apply_tesseract(image, boxes_np, classes, index)
        return image, output


#cv2.imshow('original', img)
#cv2.imwrite("temp/image.jpg",img)
#cv2.imshow('yolo_prediction', image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
#cv2.imwrite("temp/image_ocr.jpg",image)


