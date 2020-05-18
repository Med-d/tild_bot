import config
import os
import shutil
import pymysql.cursors
import telebot

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

def login_new_performer(login, password):
    pass

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

log = {}

@bot.message_handler(commands = ['login'])
def logining(message):
    global log
    bot.send_message(message.chat.id, 'enter login')
    log[message.chat.id] = {}
    bot.register_next_step_handler(message, get_login)

def get_login(message):
    global log
    log[message.chat.id][message.text] = ''
    bot.send_message(message.chat.id, 'enter password')
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    global log
    keys = log[message.chat.id]
    try:
        with connect.cursor() as cursor:
            cursor.execute('select login, pass from performer;')
            for row in cursor:
                if row['login'] == keys.keys()[0]:
                    print(1)
                    if row['pass'] == keys[keys.keys()[0]]:
                        print(2)
                        connect.execute('update performer set chat_id = '+message.chat.id+' where login = "'+keys.keys()[0]+'";')
                        connect.commit()
                        print(3)
                        bot.send_message(message.chat.id, 'ok')
                    bot.send_message(message.chat.id, 'wrong password')
            bot.send_message(message.chat.id, 'wrong login')
    except:
        bot.send_message(message.chat.id, 'something went wrong')


#Bot don't stop
if __name__ == '__main__':
     bot.polling(none_stop=True)
