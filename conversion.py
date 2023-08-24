from pdf2image import convert_from_path
import cv2
import os

def process_pdf(pdf_path):


    # Converte il PDF in immagine JPG
    images = convert_from_path(pdf_path, 500, poppler_path=r'C:\Program Files\poppler-21.11.0\Library\bin')
    print(f"Numero di immagini generate: {len(images)}")  # Stampa la lunghezza della lista images
    '''
    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save('page' + str(i) + '.jpg', 'JPEG')
    '''
    # Salva l'immagine nella cartella "temp"
    image_path = os.path.join("C:/Users/ricca/PycharmProjects/pythonProject/temp", "page.jpg")
    images[0].save(image_path, 'PNG')
    image = images[0]

    return image_path



