# -*- coding: utf-8 -*-
import config
import os
import shutil
import pymysql.cursors
import telebot
from telebot import types

#Constants
SUPER = 'super_user'
SIMPLE = 'simple_user'

#Подключение к базе данных
connect = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = config.passwordSQL,
                             db = 'users_bot',
                             charset = 'utf8',
                          cursorclass = pymysql.cursors.DictCursor)

#Ищет пользователя в таблице performer
def find_user(chat_id, username):
    with connect.cursor() as cursor:
        cursor.execute("select chat_id from performer")
        for row in cursor:
            if chat_id == row['chat_id']:
                return SUPER
        return SIMPLE

#Connecting to bot
bot = telebot.TeleBot(config.TOKEN)

def keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('FAQ')
    btn2 = types.KeyboardButton('Order')
    markup.add(btn1)
    markup.add(btn2)
    return markup

#Начало общения с ботом
@bot.message_handler(commands = ['start'])
def start_dialog(message):
    if find_user(message.chat.id, message.chat.username) == SUPER:
        bot.send_message(message.chat.id,
        "Hi, super",
        reply_markup = keyboard())
    else:
        bot.send_message(message.chat.id,
        "Hi",
        reply_markup = keyboard())

#Добавляет исполнителя. Может добавить только в том случае, если ID чата будет
#совпадать с тем, который указан в файле config.py
users = []
#
@bot.message_handler(commands = ['add_performer'])
def adding_perf(message):
    if message.chat.id == config.admin_id:
        bot.send_message(message.chat.id, "Введите login исполнителя")
        bot.register_next_step_handler(message, add_login)
    else:
        bot.send_message(message.chat.id, 'Access deneid')

def add_login(message):
    global users
    users.append(message.text)
    bot.send_message(message.chat.id, "Введите пароль для него")
    bot.register_next_step_handler(message, add_pass)

def add_pass(message):
    global users
    users.append(message.text)
    try:
        with connect.cursor() as cursor:
            cursor.execute('insert performer(login, pass) values("'+users[0]+'","'+users[1]+'");')
            connect.commit()
            bot.send_message(message.chat.id, "Исполнитель успешно добавлен!")

    except:
        bot.send_message(message.chat.id, 'something went wrong')
    users = []

#
log = {}
#
@bot.message_handler(commands = ['login'])
def logining(message):
    global log
    bot.send_message(message.chat.id, 'enter login')
    log[message.chat.id] = {}
    bot.register_next_step_handler(message, get_login)

def get_login(message):
    global log
    log[message.chat.id] = message.text
    bot.send_message(message.chat.id, 'enter password')
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    global log
    keys = {log[message.chat.id]: message.text}
    print(keys)
    try:
        with connect.cursor() as cursor:
            cursor.execute('select login, pass from performer;')
            for row in cursor:
                if row['login'] == list(keys.keys())[0]:
                    if row['pass'] == keys[list(keys.keys())[0]]:
                        cursor.execute('update performer set chat_id = '+str(message.chat.id)+' where login = "'+list(keys.keys())[0]+'";')
                        connect.commit()
                        bot.send_message(message.chat.id, 'ok')
                    else:
                        bot.send_message(message.chat.id, 'wrong password')
                else:
                    bot.send_message(message.chat.id, 'wrong login')
    except:
        bot.send_message(message.chat.id, 'something went wrong')

#Bot don't stop
if __name__ == '__main__':
     bot.polling(none_stop=True)
