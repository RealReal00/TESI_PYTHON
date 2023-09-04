import time
import threading
import asyncio
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from collections import deque
from yolo_work_4 import YOLO_Pred
from conversion import process_pdf

# Inizializza l'oggetto YOLO_Pred
yolo = YOLO_Pred('./data/best.onnx', './data.yaml')

# Crea una classe Session per memorizzare le informazioni della sessione utente
class Session:
    def __init__(self, user_id):
        self.user_id = user_id
        self.pdf_queue = deque()


# Dizionario per memorizzare le sessioni utente
session_dict = {}

# Funzione per gestire il comando /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id

    if user_id not in session_dict:
        # Se l'utente non ha una sessione, crea una nuova sessione per lui
        session = Session(user_id)
        session_dict[user_id] = session

    update.message.reply_text('Ciao! Inviami il tuo PDF')
    session_dict[user_id].standby_mode = False  # Esci dalla modalità standby quando viene inviato un PDF

# Funzione per gestire l'invio di documenti
def handle_document(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id

    if user_id not in session_dict:
        # Se l'utente non ha una sessione, crea una nuova sessione per lui
        session = Session(user_id)
        session_dict[user_id] = session

        # Esci dalla modalità standby quando viene inviato un PDF
        session.standby_mode = False

    document = update.message.document
    if document.mime_type == 'application/pdf':
        pdf_file = document.get_file()
        session_dict[user_id].pdf_queue.append(pdf_file)


# Modifica la funzione process_pdf_queue_and_send_result
async def process_pdf_queue_and_send_result():
    while True:
        for user_id, session in session_dict.items():
            if session.pdf_queue:
                pdf_files = list(session.pdf_queue)
                session.pdf_queue.clear()
                ocr_results = []

                for pdf_file in pdf_files:
                    pdf_path = f'./temp/{pdf_file.file_id}.pdf'
                    pdf_file.download(pdf_path)
                    image = process_pdf(pdf_path)
                    _, ocr_result = yolo.predictions(image)
                    ocr_results.append(ocr_result)

                global_ocr_result = '\n\n'.join(ocr_results)
                await send_ocr_result(user_id, global_ocr_result)

        await asyncio.sleep(30)  # Controlla la coda ogni 10 secondi

# Funzione per inviare il risultato OCR come messaggio
async def send_ocr_result(user_id, ocr_result):
    if ocr_result:
        bot.send_message(chat_id=user_id, text=ocr_result)
    else:
        bot.send_message(chat_id=user_id, text="Nessun risultato OCR disponibile al momento.")

# Funzione principale
def main() -> None:
    # Imposta il tuo token ottenuto da BotFather
    token = '6618676928:AAGwjEy2ljA-rlLlgyVZ1yid-ByzVqyrfB0'
    global bot
    bot = Updater(token).bot

    # Avvia il thread di elaborazione delle sessioni utente
    threading.Thread(target=asyncio.run, args=(process_pdf_queue_and_send_result(),)).start()

    # Imposta il tuo bot e dispatcher
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Aggiungi un gestore per il comando /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Aggiungi un gestore per i documenti inviati dagli utenti
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_document))

    # Avvia il bot
    updater.start_polling()
    #updater.idle()

if __name__ == '__main__':
    main()
