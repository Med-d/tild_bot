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
        cursor.execute("select chat_id from performer")
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

users = []

@bot.message_handler(commands = ['add_performer'])
def adding_perf(message):
    bot.send_message(message.chat.id, "Введите login исполнителя")
    bot.register_next_step_handler(message, add_login)

def add_login(message):
    global users
    users.append(message.text)
    bot.send_message(message.chat.id, "Введите пароль для него")
    bot.register_next_step_handler(message, add_pass)

def add_pass(message):
    users.append(message.text)
    try:
        with connect.cursor() as cursor:
            cursor.execute('insert performer(login, pass) values("'+users[0]+'","'+users[1]+'");')
            bot.send_message(message.chat.id, "Исполнитель успешно добавлен!")
    except:
        bot.send_message(message.chat.id, 'somthing went wrong')

#Bot don't stop
if __name__ == '__main__':
     bot.polling(none_stop=True)
