import tempfile
import threading
import time
from telegram import Update, update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from collections import deque
from yolo_work import YOLO_Pred
from bot_time import pdf_queue
from conversion import process_pdf

yolo = YOLO_Pred('./data/best.onnx', './data.yaml')  # Inizializza l'oggetto YOLO_Pred
yolo.predictions('./temp/page.jpg')