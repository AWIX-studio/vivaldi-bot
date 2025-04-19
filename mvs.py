import telebot
import os
import requests
import source.bpm_detect

bot = telebot.TeleBot('7414108235:AAGOilxSXgIVZcXTa4ewGI7DZSPbjx9YP-8')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "Audio")

# Если какой-то умник удалит папку
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Привет. Я Вивальди бот. Я создан, чтобы немного упростить тебе работу с музыкой. Пришли мне свой аудиофайл и я скажу, что я могу с ним сделать (или напиши /help чтобы получить информацию по всем моим возможностям).')

# Получение текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'Coming soon...')

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    try:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio_file.mp3"
        
        # Скачивание файла
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            raise ConnectionError("Не удалось скачать файл")
        
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Анализ BPM
        try:
            bpm = source.bpm_detect.BPM_Detector(file_path)
            bpm_value = f"{round(float(bpm.tempo))} ({round(float(bpm.tempo) * 2)})"
            bot.reply_to(message, f"🎵 BPM трека: {bpm_value}")
            
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка анализа: {str(e)}")
            
    except Exception as e:
        bot.reply_to(message, f"🚫 Критическая ошибка: {str(e)}")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

bot.polling(none_stop=True, interval=0)
