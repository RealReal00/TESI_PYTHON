import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from yolo_work import YOLO_Pred
from conversion import process_pdf

yolo = YOLO_Pred('./data/best.onnx', './data.yaml')  # Inizializza l'oggetto YOLO_Pred


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ciao! Inviami il tuo PDF')

def handle_incoming_pdf(update: Update, context: CallbackContext) -> None:
    if update.message.document and update.message.document.mime_type == 'application/pdf':
        pdf_content = update.message.document.get_file().download_as_bytearray()
        image = process_pdf(pdf_content)


        image_data, result = yolo.predictions(image)
        # Invia l'immagine come foto
        update.message.reply_photo(photo=image_data, caption=f'Result: {result}')


def main() -> None:
    # Imposta il tuo token ottenuto da BotFather
    token = '6618676928:AAGwjEy2ljA-rlLlgyVZ1yid-ByzVqyrfB0'
    updater = Updater(token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_incoming_pdf))

    updater.start_polling()

    # Mantieni il bot in esecuzione
    updater.idle()



if __name__ == '__main__':
    main()
