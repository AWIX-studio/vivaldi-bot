# coding=utf-8

import telebot
from telebot import types

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == 'ras':
        bot.send_message(message.from_user.id, 'svet')
#    elif message.text == 'капли крови в раю':
#        bot.send_message(message.from_user.id, 'может вместе сдохнем')
#    elif message.text == 'я уверен что смогу':
#        bot.send_message(message.from_user.id, 'может вместе сдохнем')
#    elif message.text == 'убить нас двоих в саду':
#        bot.send_message(message.from_user.id, 'может вместе сдохнем')

bot.polling(none_stop=True, interval=0)