# coding=utf-8





import telebot


from telebot import types





bot = telebot.TeleBot('7414108235:AAGOilxSXgIVZcXTa4ewGI7DZSPbjx9YP-8')


@bot.message_handler(commands=['sendfile'])
def send_document(message):
    with open('может вместе сдохнем.mp3', 'rb') as audio:
        bot.send_audio(message.chat.id, audio)


@bot.message_handler(content_types=['text'])


def get_text_messages(message):





    if message.text == 'расцветает весна в аду':


        bot.send_message(message.from_user.id, 'может вместе сдохнем')


    elif message.text == 'капли крови в раю':


        bot.send_message(message.from_user.id, 'может вместе сдохнем')


    elif message.text == 'я уверен что смогу':


        bot.send_message(message.from_user.id, 'может вместе сдохнем')


    elif message.text == 'убить нас двоих в саду':


        bot.send_message(message.from_user.id, 'может вместе сдохнем')





bot.polling(none_stop=True, interval=0)
