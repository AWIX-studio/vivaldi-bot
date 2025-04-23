import telebot
import os
import requests
from telebot.apihelper import send_audio
import source.bpm_detect
import source.pitchShifter
from dotenv import load_dotenv
from telebot import types
import time

# neural-stem-slicer
import neuralStemSlicer.step1_BPMAnalysis
import neuralStemSlicer.step2_KeyAnalysis
import neuralStemSlicer.step3_1_StemSeperation

load_dotenv()
bot = telebot.TeleBot(str(os.getenv('BOT_TOKEN')))
telebot.apihelper.delete_webhook(bot.token)
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "Audio")

# Хранилище для последних сообщений с кнопками
user_last_messages = {}

# Хранилище данных после запроса на pitch
user_states = {}

# Если какой-то умник удалит папку
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, '''Привет. Я Вивальди бот.
Я создан, чтобы немного упростить тебе работу с музыкой.
Пришли мне свой аудиофайл и я скажу, что я могу с ним сделать
(или напиши /help чтобы получить информацию по всем моим возможностям).''')

# Получение текстовых сообщений
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, 'Coming soon...')

# Получаем аудиофайл
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    try:
        file_id = message.audio.file_id
        original_file_name = message.audio.file_name or "audio_file.mp3"
        chat_id = message.chat.id

        # Генерируем уникальный ID для файла (чтобы не передавать file_id)
        safe_file_name = original_file_name.replace(" ", "_").replace(".", "_")[:20]
        unique_file_id = f"{chat_id}_{int(time.time())}"
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{unique_file_id}.mp3")

        # Скачиваем файл
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        response = requests.get(file_url)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)

        # Анализ BPM и Key
        y, sr = neuralStemSlicer.step1_BPMAnalysis.detect_y_sr(file_path)
        bpm = neuralStemSlicer.step1_BPMAnalysis.detect_bpm(y, sr, file_path)[0]
        key = neuralStemSlicer.step2_KeyAnalysis.detect_key(file_path)

        # Создаём кнопки с сокращённым callback_data
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(
                'Разделить по дорожкам', 
                callback_data=f'stem|{unique_file_id}'  # Только действие и ID
            ),
            types.InlineKeyboardButton(
                'Изменить питч', 
                callback_data=f'pitch|{unique_file_id}'
            )
        )

        # Удаляем предыдущее сообщение (если есть)
        if chat_id in user_last_messages:
            try:
                bot.delete_message(chat_id, user_last_messages[chat_id])
            except:
                pass
                
        # Отправляем новое сообщение
        msg = bot.reply_to(
            message,
            f'''Информация о файле:\n*BPM:* {bpm}\n*Key:* {key[0][1]}\n\n
            Выберите дальнейшее действие:''',
            parse_mode="Markdown",
            reply_markup=markup
        )
        user_last_messages[chat_id] = msg.message_id
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    try:
        data_parts = call.data.split('|')
        print(data_parts)
        action = data_parts[0]
        unique_file_id = data_parts[1]
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{unique_file_id}.mp3")

        if action == 'stem':
            bot.send_message(call.message.chat.id, "Начинаю разделение на дорожки...")
            # Здесь обработка файла из file_path
            neuralStemSlicer.step3_1_StemSeperation.separate_stems(
                    file_path, fr'out/{unique_file_id}'
                    )
            files = os.listdir(f'out/{unique_file_id}/')
            bot.send_message(call.message.chat.id, "Выполнено!")
            for file in files:
                with open(f'out/{unique_file_id}/{file}', 'rb') as sending_file:
                    bot.send_audio(call.message.chat.id, sending_file)
            os.remove(file_path)
            for file in files:
                os.remove(f'out/{unique_file_id}/{file}')
            os.rmdir(f'out/{unique_file_id}')
            
        elif action == 'pitch':
            bot.send_message(call.message.chat.id, '''Введите количество центов (число).
__Примечание: если хотите замедлить песню, нужно вводить отрицательное значение__''',
                             parse_mode="Markdown"
                             )
            # Здесь обработка файла из file_path
            user_states[call.from_user.id] = {
                    'waiting_for_pitch' : True,
                    'file_id' : unique_file_id,
                    'chat_id' : call.message.chat.id,
                    'file_path' : file_path,
                    'unique_file_id' : unique_file_id,
            }
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка: {str(e)}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        if user_states[message.from_user.id]['waiting_for_pitch']:

            cent = int(message.text)
            bot.send_message(message.chat.id, 'Выполняю...')

            file_path = user_states[message.from_user.id]['file_path']
            unique_file_id = user_states[message.from_user.id]['unique_file_id']
            out_path = fr'(+{cent}) {unique_file_id}'
            source.pitchShifter.change_pitch_with_speed(file_path, out_path, cent)
            print('код выполнился')
            with open(out_path, 'rb') as sending_file:
                bot.send_message(message.chat.id, 'Готово!')
                bot.send_audio(message.chat.id, sending_file)

            os.remove(file_path)
            os.remove(out_path)
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
bot.polling(none_stop=True, interval=0)
