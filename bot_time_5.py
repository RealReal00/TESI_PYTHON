import time
import threading
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from collections import deque
from yolo_work_4 import YOLO_Pred
from conversion import process_pdf



yolo = YOLO_Pred('./data/best.onnx', './data.yaml')  # Inizializza l'oggetto YOLO_Pred

pdf_queue = deque()  # Coda per i file PDF
processing_thread = None  # Thread per l'elaborazione dei PDF

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ciao! Inviami il tuo PDF')

def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    if document.mime_type == 'application/pdf':
        pdf_file = document.get_file()
        pdf_queue.append(pdf_file)

def process_pdf_queue():
    global processing_thread

    while True:
        if pdf_queue:
            pdf_file = pdf_queue.popleft()
            pdf_path = f'./temp/{pdf_file.file_id}.pdf'
            pdf_file.download(pdf_path)
            image = process_pdf(pdf_path)
            yolo.predictions(image)
        else:
            time.sleep(5)  # Attendi 10 secondi se la coda è vuota

def main() -> None:
    # Imposta il tuo token ottenuto da BotFather
    token = '6618676928:AAGwjEy2ljA-rlLlgyVZ1yid-ByzVqyrfB0'
    updater = Updater(token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_document))

    # Avvia il thread di elaborazione dei PDF
    global processing_thread
    processing_thread = threading.Thread(target=process_pdf_queue)
    processing_thread.start()

    updater.start_polling()

    # Mantieni il bot in esecuzione
    updater.idle()

if __name__ == '__main__':
    main()
