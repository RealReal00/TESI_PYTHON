import tempfile
import threading
import time
from telegram import Update, update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from collections import deque
from yolo_workechoee_1 import YOLO_Pred
from bot_time import pdf_queue
from conversion import process_pdf

yolo = YOLO_Pred('./data/best.onnx', './data.yaml')  # Inizializza l'oggetto YOLO_Pred


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ciao! Inviami il tuo PDF')

'''
def handle_pdf(update, context):
    pdf_file = update.message.document  # Ottieni l'oggetto File del PDF inviato
    temp_pdf_path = os.path.join("./temp", pdf_file.file_name)

    # Salva il PDF nella cartella temporanea
    pdf_file.get_file().download(temp_pdf_path)
'''
'''
def handle_incoming_pdf(update: Update, context: CallbackContext) -> None:
    if update.message.document and update.message.document.mime_type == 'application/pdf':
        pdf_content = update.message.document.get_file().download_as_bytearray()
        image = process_pdf(pdf_content)

        # Salva il PDF nella cartella temporanea "temp"
        pdf_path = os.path.join("C:/Users/ricca/PycharmProjects/pythonProject/temp", "input.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_content)

       # image_data, result = yolo.predictions(image)
        # Invia l'immagine come foto
        #update.message.reply_photo(photo=image_data, caption=f'Result: {result}')
'''

def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    if document.mime_type == 'application/pdf':
        print("entro")
        # Salva il contenuto del documento in un file temporaneo
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(document.get_file().download_as_bytearray())
            temp_file_path = temp_file.name
            print(temp_file_path)
        pdf_queue.append(temp_file_path)
        print(temp_file_path)
        image = process_pdf(temp_file_path)
        yolo.predictions(image)


def main() -> None:
    # Imposta il tuo token ottenuto da BotFather
    token = '6618676928:AAGwjEy2ljA-rlLlgyVZ1yid-ByzVqyrfB0'
    updater = Updater(token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    #dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_incoming_pdf))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_document))

    updater.start_polling()

    # Mantieni il bot in esecuzione
    updater.idle()



if __name__ == '__main__':
    main()
