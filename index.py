import config
import telebot
import os
import shutil
import pymysql.cursors

#Constants
SUPER = 'super_user'
SIMPLE = 'simple_user'

connect = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = config.passwordSQL,
                             db = 'users_bot',
                             charset = 'utf8',
                          cursorclass = pymysql.cursors.DictCursor)

def find_user(chat_id, username):
    with connect.cursor() as cursor:
        cursor.execute("select chat_id from perfomer")
        for row in cursor:
            if chat_id == row['chat_id']:
                return SUPER
        return SIMPLE

#Connecting to bot
bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def start_dialog(message):
    if find_user(message.chat.id, message.chat.username) == SUPER:
        bot.send_message(message.chat.id, "Hi, super")
    else:
        bot.send_message(message.chat.id, "Hi")
