import psycopg2
from conf_main import host, user, password, db_name
import json
import time
import datetime
from datetime import date
import secrets

def errors(er):
    
     print(er)


# CREATE DB

connection =  psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

# Создание таблиц
def create_db():
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE users")
        cursor.execute("DROP TABLE chats")
        #cursor.execute("DROP TABLE chat_0")
        #cursor.execute("DROP TABLE chat_1")
        #cursor.execute("DROP TABLE chat_2")
        cursor.execute(""" CREATE TABLE IF NOT EXISTS users  (
                       user_id INT PRIMARY KEY NOT NULL,
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL, 
                       email VARCHAR(255) NOT NULL, 
                       password VARCHAR(127) NOT NULL,
                       user_chats INT NOT NULL,
                       user_token VARCHAR(256) NOT NULL)""")  
        cursor.execute(""" CREATE TABLE IF NOT EXISTS chats (
                       chat_id INT PRIMARY KEY NOT NULL,
                       user_id_1 INT NOT NULL,
                       user_id_2 INT NOT NULL)""")
       
        connection.commit()
# create_db()

def load_last_mesasage(chat_id):
    with connection.cursor() as cursor:
        last_mes = cursor.execute(f" SELECT type, message FROM chat_{chat_id} ORDER BY message_id DESC LIMIT 1 ")
        last_mes = cursor.fetchone()
        if last_mes == 'file':
             return "Файл"
        if last_mes != None:
            return last_mes[1]
        else:
             return ""
     

def chek_token_db(user_id, token):
     with connection.cursor() as cursor:
          cursor.execute(f" SELECT user_token FROM users WHERE user_id = {user_id}")
          token_bd = cursor.fetchone()
          if token_bd == token or token_bd[0] == token:
               return "Токен_подтверждён"
          else:
               return "Токен_неверен"


def login_db(password, email):
        with connection.cursor() as cursor:
            cursor.execute(f""" SELECT user_id, first_name, last_name, email, user_token FROM users WHERE email = '{email}' and password = '{password}'""")
            user = cursor.fetchone()
            if user != None:
                return user
            else:
                  return False
             



def load_len_user_chats(user_id, user_chat):
    with connection.cursor() as cursor:
        cursor.execute(f""" SELECT user_chats FROM users WHERE user_id = {user_id}""")
        MAX_user_chat = cursor.fetchone()
        if user_chat == MAX_user_chat[0] or user_chat == MAX_user_chat:
             return 'Обновлений нет'
        else:
             return 'Обновления есть'

# Возвращает chat_id всех чатов  (вместе с id юзеровц) юзера по id 
def load_chats_id(user_id):
    with connection.cursor() as cursor:
           
            cursor.execute(f""" SELECT chat_id, user_id_1, user_id_2 FROM chats WHERE user_id_1 = {user_id} or user_id_2 = {user_id}""")
            chats = cursor.fetchall()
            return chats



# Возвращет вс сообщения, доработать
def load_one_chat(chat_id):
    try:
        
        with connection.cursor() as curosr:
             curosr.execute(f""" SELECT * FROM chat_{chat_id}""")
             chat = curosr.fetchall()
             return chat
    except Exception as er:
         errors(er)
         return "error"
    


# Возвращает user_id по email метод from_create_chat
# Возвращает user_id first_name, last_name по email метод from_find_user
def find_user_db(email, method):
     with connection.cursor() as cursor:
            if method == "from_create_chat":
                cursor.execute(f""" SELECT user_id FROM users WHERE email = '{email}'""")
                user_id_fr_db = cursor.fetchone()
                if user_id_fr_db[0] != None:
                    user_id_2 = user_id_fr_db[0]
                    return user_id_2
                else:
                    return False
            elif method == "from_find_user":
                cursor.execute(f""" SELECT  user_id, first_name, last_name FROM users WHERE email = '{email}'""")
                user = cursor.fetchone()              
                return user
            
def find_info_user_id_2_db(user_id):
     with  connection.cursor() as  cursor:
        cursor.execute(f""" SELECT  user_id, first_name, last_name, email FROM users WHERE user_id = {user_id}""")
        user = cursor.fetchone()              
        return user

def find_user_db_from_user_id(user_id):
     with connection.cursor() as cursor:
        cursor.execute(f""" SELECT  user_id, first_name, last_name FROM users WHERE user_id = {user_id}""")
        user = cursor.fetchone()
        return user

# Возвращает chat_id по id двух человек
def take_one_chat_id(user_id_1, user_id_2):
     with connection.cursor() as cursor:
        if user_id_1 < user_id_2:
            user_id_1 = user_id_1
        else: 
            user_id_ch = user_id_1
            user_id_1 = user_id_2
            user_id_2 = user_id_ch
    
        cursor.execute(f""" SELECT chat_id FROM chats WHERE user_id_1 = {user_id_1} and user_id_2 = {user_id_2}""")
        chat_id = cursor.fetchone()
    
        if chat_id != None:
            chat_id = chat_id[0]
           
            return chat_id
        return chat_id



# Выполняет фунции для создания чата (в таблице chats информацию о чате и таблицу чата)
def create_chat(user_id_1, user_id_2):
    try: 
        with connection.cursor() as cursor:
                cursor.execute(""" SELECT MAX(chat_id) FROM chats""")
                chat_id = cursor.fetchone()
                if chat_id[0] == None:
                        chat_id = 0
                else:
                    chat_id = chat_id[0] + 1
                cursor.execute(f""" SELECT user_id FROM users WHERE user_id = {user_id_1} or user_id = {user_id_2}""")
                users = cursor.fetchall()
                if len(users) != 2:
                     return "Такой пользователь не зарегестирован"

                if user_id_1 < user_id_2:
                        user_id_1 = user_id_1
                else: 
                        user_id_ch = user_id_1
                        user_id_1 = user_id_2
                        user_id_2 = user_id_ch
            
                cursor.execute(f""" INSERT INTO chats(chat_id, user_id_1, user_id_2)
                                VALUES({chat_id}, {user_id_1}, {user_id_2})""")
                cursor.execute(f""" CREATE TABLE IF NOT EXISTS chat_{chat_id}(
                                user_id INT NOT NULL,
                                message_id INT PRIMARY KEY NOT NULL,
                                type VARCHAR(127) NOT NULL,
                                message VARCHAR(4095) NOT NULL,
                                
                                date_message DATE NOT NULL,
                                time_message TIME NOT NULL)""")  
                
                def update_user_chats(user_id):
                    cursor.execute(f""" SELECT user_chats FROM users WHERE user_id = {user_id}""")
                    max_chat = cursor.fetchone()

                    if max_chat[0] == None or max_chat == None:
                        max_chat = 1
                    else:
                        max_chat = max_chat[0] + 1
                    
                    cursor.execute(f""" UPDATE users SET user_chats = {max_chat} WHERE user_id = {user_id} """)
                update_user_chats(user_id_1)
                update_user_chats(user_id_2)            
                connection.commit()
    except Exception as er:
        errors(er)

# сохраняет сообщение в БД
def send_message(user_id, text, chat_id, type_mes):
    date_message = date.today()
    time_message = datetime.datetime.now().strftime('%H:%M:%S')
    with connection.cursor() as cursor:       
                cursor.execute(f""" SELECT  MAX(message_id)  FROM chat_{chat_id}""")
                message_id = cursor.fetchone()
                if message_id[0] == None or message_id == None:
                        message_id = 1
                else:
                       message_id = message_id[0] + 1                
                cursor.execute(f""" INSERT INTO chat_{chat_id}( user_id, message_id, type, message, date_message, time_message)
                       VALUES ({user_id}, {message_id}, '{type_mes}', '{text}', '{date_message}', '{time_message}')""")  
                connection.commit()
# Принимает максимальный id сообщения и сверяет его с максимальным из БД
def chek_updates_message(chat_id, message_id_MAX):
     with connection.cursor() as cursor:
        cursor.execute(f""" SELECT MAX(message_id)  FROM chat_{chat_id}""")
        message_id = cursor.fetchone()
        if message_id_MAX == message_id[0] or message_id_MAX == message_id or message_id[0] == None:
             return 'Обновлений нет'
        else:
             return 'Обновления есть'


# Регистрирует пользователя 
def reg_db(first_name, last_name, email, password):
    try:          
        try:            
            with connection.cursor() as cursor:
                cursor.execute(""" SELECT MAX(user_id) from users""")
                user_id = cursor.fetchone()
                if user_id[0] == None or user_id == None:
                     user_id = 0
                else:
                     user_id = user_id[0] + 1 
            connection.commit()           
        except Exception as ex:
            errors(ex)
        user_token = secrets.token_urlsafe()
        try:            
            with connection.cursor() as cursor:
                cursor.execute(f""" INSERT INTO users (user_id, first_name, last_name, email, password, user_chats, user_token)
                            VALUES({user_id}, '{first_name}', '{last_name}', '{email}', '{password}', 0, '{user_token}') """)
            connection.commit()
        except Exception as ex:
            errors(ex)             
    except Exception as ex:
            errors(ex)
    return [user_id, user_token]
