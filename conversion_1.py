from pdf2image import convert_from_bytes

def convert_pdf_to_images(pdf_data):
    images = convert_from_bytes(pdf_data)
    return images

# Esempio di come potresti utilizzare la funzione
with open('example.pdf', 'rb') as pdf_file:
    pdf_data = pdf_file.read()
    images = convert_pdf_to_images(pdf_data)

for i, image in enumerate(images):
    image.save(f'page{i}.jpg', 'JPEG')
