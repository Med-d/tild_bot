import config
import telebot
import os
import shutil
import pymysql.cursors

connect = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = config.passwordSQL,
                             db = 'active_users',
                             charset = 'utf8',
                          cursorclass = pymysql.cursors.DictCursor)

def find_user(chat_id, username):
    with connect.cursor() as cursor:
        cursor.execute("select chat_id from super_users")
        for row in cursor:
            if chat_id == row['chat_id']:
                return SUPER
        cursor.execute("select chat_id from simple_users")
        for row in cursor:
            if chat_id == row['chat_id']:
                return SIMPLE
        cursor.execute("insert simple_users(chat_id, name) values ("+str(chat_id)+", '"+str(username)+"');")
        return SIMPLE

#Connecting to bot
bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def start_dialog(message):
