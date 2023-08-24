from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from aaa import output


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ciao! Inviami un file PDF.')


def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    if document.mime_type == 'application/pdf':
        file_id = document.file_id
        file_name = document.file_name

        # Qui puoi eseguire le azioni desiderate sul file PDF.
        update.message.reply_text(f'Hai inviato un file PDF: "document"')
        update.message.reply_text("Ora ti mostro i titoli più importanti del documento")
        update.message.reply_text(output)
    else:
        update.message.reply_text('Inviami solo file PDF.')


def main():
    # Sostituisci 'YOUR_BOT_TOKEN' con il token del tuo bot
    updater = Updater(token='6618676928:AAGwjEy2ljA-rlLlgyVZ1yid-ByzVqyrfB0', use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type('application/pdf'), handle_document))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
