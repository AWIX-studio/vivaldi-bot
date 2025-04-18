import telebot
from telebot import types

bot = telebot.TeleBot('7414108235:AAGOilxSXgIVZcXTa4ewGI7DZSPbjx9YP-8')

@bot.message_handler(commands=['sendfile'])
def send_document(message):
    with open('может вместе сдохнем.mp3', 'rb') as audio:
        bot.send_audio(message.chat.id, audio)

bot.polling(none_stop=True, interval=0)
