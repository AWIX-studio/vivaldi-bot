import telebot
import os
import requests
from telebot import types

bot = telebot.TeleBot('7414108235:AAGOilxSXgIVZcXTa4ewGI7DZSPbjx9YP-8')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "Audio")

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Привет. Я Вивальди бот. Я создан, чтобы немного упростить тебе работу с музыкой. Пришли мне свой аудиофайл и я скажу, что я могу с ним сделать (или напиши /help чтобы получить информацию по всем моим возможностям).')

# Получение текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'Coming soon...')

# Получение аудиофайла
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    file_id = None
    file_name = "audio_file"
    
    # Распознание типа файла
    if message.content_type == 'audio':
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio.mp3"
    if not file_id:
        bot.reply_to(message, "Это не аудиофайл!")
        return
    
    # Получение ссылки на файл
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
    
    # Скачивание аудио
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        bot.reply_to(message, f"✅ Аудио сохранено как: `{file_name}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Ошибка при скачивании файла")

bot.polling(none_stop=True, interval=0)
