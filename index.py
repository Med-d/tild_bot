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
def find_user(chat_id):
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
    btn2 = types.KeyboardButton("Сделать заказ")
    markup.add(btn2, btn1)
    return markup

def keyboard_accept():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('Accept')
    btn2 = types.KeyboardButton("Deny")
    markup.add(btn2, btn1)
    return markup

def push_order(short_ord):
    with connect.cursor() as cursor:
        cursor.execute('select chat_id from performer;')
        for row in cursor:
            bot.send_message(row['chat_id'], 'New order! Short name: ' + short_ord)

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
    #bot.send_message(message.chat.id, message.chat.id)
    if str(message.chat.id) == config.admin_id:
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
    f = True
    try:
        with connect.cursor() as cursor:
            cursor.execute('select login, pass from performer;')
            for row in cursor:
                if row['login'] == list(keys.keys())[0]:
                    if row['pass'] == keys[list(keys.keys())[0]]:
                        cursor.execute('update performer set chat_id = '+str(message.chat.id)+' where login = "'+list(keys.keys())[0]+'";')
                        connect.commit()
                        bot.send_message(message.chat.id, 'ok')
                        f = False
                    else:
                        bot.send_message(message.chat.id, 'wrong password')
            if f:
                bot.send_message(message.chat.id, 'wrong login')
    except:
        bot.send_message(message.chat.id, 'something went wrong')
    log.pop(message.chat.id)

orders = {}

id = {}

@bot.message_handler(commands = ['find_order'])
def start_finding(message):
    if find_user(message.chat.id) == SUPER:
        bot.send_message(message.chat.id, 'Enter short name of order to get information')
        bot.register_next_step_handler(message, find_order)
    else:
        bot.send_message(message.chat.id, 'Access denied')

def find_order(message):
    global id
    f = True
    with connect.cursor() as cursor:
        cursor.execute('select id, short_ord, ord, contacts from orders')
        for row in cursor:
            if row['short_ord'] == message.text:
                bot.send_message(message.chat.id,
                'Order: \n' + row['ord'],
                reply_markup = keyboard_accept())
                id[message.chat.id] = row['contacts']

def get_contact(message):
    global id
    if message.text == 'Accept':
        bot.send_message(message.chat.id, "Contacts: "+id[message.chat.id])
    else:
        bot.send_message(message.chat.id, "Order deneid")

@bot.message_handler(content_types = ['text'])
def simple_text(message):
    if message.text.lower() == "сделать заказ":
        bot.send_message(message.chat.id, 'Enter sortcut name of order')
        bot.register_next_step_handler(message, short_name)
    elif message.text.lower() == 'faq':
        bot.send_message(message.chat.id,
        'FAQ',
        reply_markup = keyboard())
    else:
        bot.send_message(message.chat.id, 'don`t understand')

def short_name(message):
    global orders
    orders[message.chat.id] = [message.text]
    bot.send_message(message.chat.id, 'Enter full information about order')
    bot.register_next_step_handler(message, order_inf)

def order_inf(message):
    global orders
    orders[message.chat.id].append(message.text)
    bot.send_message(message.chat.id, 'Enter your contacts')
    bot.register_next_step_handler(message, contact_add_bd)

def contact_add_bd(message):
    global orders
    orders[message.chat.id].append(message.text)
    keys = orders.pop(message.chat.id)
    try:
        with connect.cursor() as cursor:
            cursor.execute('insert orders(short_ord, ord, contacts) values ("'+keys[0]+'", "'+keys[1]+'", "'+keys[2]+'")')
            connect.commit()
            push_order(keys[0])
            bot.send_message(message.chat.id, 'order has been added')
    except:
        bot.send_message(message.chat.id, 'something went wrong')



#Bot don't stop
if __name__ == '__main__':
     bot.polling(none_stop=True)
