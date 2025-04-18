import telebot
from telebot import types

bot = telebot.TeleBot('7414108235:AAGOilxSXgIVZcXTa4ewGI7DZSPbjx9YP-8')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Привет. Я Вивальди бот. Я создан, чтобы немного упростить тебе работу с музыкой. Пришли мне свой аудиофайл и я скажу, что я могу с ним сделать (или напиши /help чтобы получить информацию по всем моим возможностям).')

@bot.message_handler(content_types=['text','audio', 'voice', 'document'])
def get_text_messages(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'Coming soon...')
    if message.content_type == 'audio':
        file_id = message.audio.file_id
        bot.reply_to(message, 'Получил твою музыку! Слушай, ну и парашу же ты слушаешь, чувак...')



bot.polling(none_stop=True, interval=0)
