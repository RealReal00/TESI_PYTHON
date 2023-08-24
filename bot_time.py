import tempfile
import threading
import time
from telegram import Update, update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from collections import deque
from aaa_classi import YOLO_Pred
from conversion import process_pdf

pdf_queue = deque()  # Coda per accumulare i PDF inviati negli ultimi 10 secondi
yolo = YOLO_Pred('./data/best.onnx', './data.yaml')  # Inizializza l'oggetto YOLO_Pred

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ciao! Inviami uno o più file PDF.')

def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    if document.mime_type == 'application/pdf':
        # Salva il contenuto del documento in un file temporaneo
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(document.get_file().download_as_bytearray())
            temp_file_path = temp_file.name
        pdf_queue.append(temp_file_path)


def process_pdf(pdf_document):
    # Carica il contenuto del PDF e passalo a apply_tesseract
    pdf_content = pdf_document.get_file().download_as_bytearray()
    _, pdf_output = yolo.predictions(pdf_content)
    return pdf_output

def process_pdfs(update: Update, context: CallbackContext) -> None:
    while True:
        if pdf_queue:
            pdfs_to_process = list(pdf_queue)
            pdf_queue.clear()

            combined_output = ""  # Variabile per accumulare l'output di tutti i PDF

            for pdf_path in pdfs_to_process:


                # Esegui l'elaborazione del PDF
                pdf_output = process_pdf(pdf_path)  # Sostituisci con il codice di elaborazione reale

                # Accumula l'output di tutti i PDF
                combined_output += pdf_output + "\n\n"  # Aggiungi due accapi tra i PDF

            # Invia l'output combinato come risposta
            if combined_output:
                context.bot.send_message(chat_id=context.job.context, text=combined_output)
            else:
                context.bot.send_message(chat_id=context.job.context, text="Nessun PDF elaborato.")

        time.sleep(10)  # Attendi 10 secondi prima di eseguire nuovamente l'elaborazione

def main():
    # Sostituisci 'YOUR_BOT_TOKEN' con il token del tuo bot
    updater = Updater(token='6618676928:AAGwjEy2ljA-rlLlgyVZ1yid-ByzVqyrfB0', use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type('application/pdf'), handle_document))

    # Aggiungi la funzione process_pdfs come job pianificato
    job_queue = updater.job_queue
    job_queue.run_repeating(process_pdfs, interval=10, first=0, context=update.Message.chat_id)


    updater.start_polling()

    # Avvia il thread per l'elaborazione ciclica dei PDF
    pdf_processing_thread = threading.Thread(target=process_pdfs)
    pdf_processing_thread.start()

    updater.idle()

if __name__ == '__main__':
    main()
