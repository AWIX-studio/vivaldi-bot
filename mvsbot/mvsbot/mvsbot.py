# coding=utf-8

import telebot
from telebot import types

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == 'ras':
        bot.send_message(message.from_user.id, 'svet')
#    elif message.text == '����� ����� � ���':
#        bot.send_message(message.from_user.id, '����� ������ �������')
#    elif message.text == '� ������ ��� �����':
#        bot.send_message(message.from_user.id, '����� ������ �������')
#    elif message.text == '����� ��� ����� � ����':
#        bot.send_message(message.from_user.id, '����� ������ �������')

bot.polling(none_stop=True, interval=0)