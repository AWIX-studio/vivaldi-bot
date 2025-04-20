import telebot
import os
import requests
import source.bpm_detect
from dotenv import load_dotenv
from telebot import types

# neural-stem-slicer
import neuralStemSlicer.step1_BPMAnalysis
import neuralStemSlicer.step2_KeyAnalysis

load_dotenv()
bot = telebot.TeleBot(str(os.getenv('BOT_TOKEN')))
telebot.apihelper.delete_webhook(bot.token)
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "Audio")

# Хранилище для последних сообщений с кнопками
user_last_messages = {}

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
 
# Реакция бота на нажатие кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == 'StemSlice':
        bot.send_message(call.message.chat.id, "Пон")
    if call.data == 'Pitch':
        bot.send_message(call.message.chat.id, "А в рожу получить не хочешь?")

# Получаем аудиофайл
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    
    try:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio_file.mp3"
        chat_id = message.chat.id

        # Скачивание файла
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            raise ConnectionError("Не удалось скачать файл")
        bot.send_message(message.from_user.id, 'Получил твой файл. Обрабатываю...')
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Анализ BPM
        """
        try:
            bpm = source.bpm_detect.BPM_Detector(file_path).tempo
            if bpm > 100:
                bpm_value = f'{round(float(bpm))}'
            else:
                bpm_value = f"{round(float(bpm))} ({round(float(bpm) * 2)})"
            bot.reply_to(message, f"🎵 BPM трека: {bpm_value}")
            
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка анализа: {str(e)}")
        """
        
        # Анализ от neuralStemSlicer
        try:
            # BPM
            y, sr = neuralStemSlicer.step1_BPMAnalysis.detect_y_sr(file_path)
            bpm = neuralStemSlicer.step1_BPMAnalysis.detect_bpm(y, sr, file_path)[0]
            
            # Key
            key = neuralStemSlicer.step2_KeyAnalysis.detect_key(file_path)

            # Создаем новую клавиатуру
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Разделить по дорожкам', callback_data='StemSlice'))
            markup.add(types.InlineKeyboardButton('Изменить питч', callback_data='Pitch'))

            # Удаляем предыдущее сообщение с кнопкой (если есть)
            if chat_id in user_last_messages:
                try:
                    bot.delete_message(chat_id, user_last_messages[chat_id])
                except:
                    pass
            
            # Отправляем пользователю файл с возможностью дальнейших действий
            msg = bot.reply_to(message, f"Информация о твоём файле \n\nBPM: {bpm} \nKey: {key[0][1]}\nЧто хочешь сделать с ним?", reply_markup=markup)
            
            # Сохраняем ID нового сообщения
            user_last_messages[chat_id] = msg.message_id

        except Exception as e:
            bot.reply_to(message, f'ошибка: {str(e)}')

    except Exception as e:
        bot.reply_to(message, f"🚫 Критическая ошибка: {str(e)}")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

bot.polling(none_stop=True, interval=0)
