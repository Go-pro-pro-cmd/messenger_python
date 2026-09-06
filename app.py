import flask
from flask import Flask, send_file,render_template, url_for, request, redirect, jsonify, send_from_directory
import json
from db_main import find_user_db_from_user_id,  load_last_mesasage, chek_token_db, reg_db, login_db, find_info_user_id_2_db,  load_chats_id, load_one_chat, send_message, create_chat, find_user_db, take_one_chat_id, send_message, chek_updates_message, load_len_user_chats
from files import save_file
from logik import chek_create_chat
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import os



# Настройка отправки почты
#======================
sender_email = "Ваша почта"
app_password = "пароль для яндекст почты, найти по инструкции из интернета" 
# =====================

email_nums = {}
application = Flask(__name__)


def errors(er):
    return render_template('error.html', er=er)





# Страница с выбором входа или регистрации
@application.route('/', methods=['POST', 'GET'])
def start_page():
     return render_template('start_page.html')



@application.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        us_inf = request.get_json()
        email = us_inf['email']
        password = us_inf['password'] 
        user = login_db(password, email)
        if user != False and user != None:
            first_name = user[1]
            last_name = user[2]
            user_id = user[0]
            token = user[4]
            return render_template('next_step.html', user_id=user_id, first_name=first_name, last_name=last_name, email=email, token=token)
        else:
             return render_template('login.html', user_states="Проверьте правильность введённых данных")

    return render_template('login.html', user_states="")
         



# Страница регистрации с функцией обработки данных регистрации
@application.route('/registration', methods=['POST', 'GET'])
@application.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = str(request.form['email'])
        email_chek = request.form['email_chek']
        password = request.form['password']
        if email_chek == email_nums[email]:
            del email_nums[email]
            user_id = reg_db(first_name, last_name, email, password)
        
            return render_template('next_step.html', user_id=user_id[0], first_name=first_name, last_name=last_name, email=email, token=user_id[1])
        else:
             return render_template('reg.html', code_states="Код с почты не верен, попробуйте снова")
    else: 
              return render_template('reg.html', code_states="")
    
# Обрабатывает почту
@application.route('/email_chek/<string:email>')
def chek_email(email):
    receiver_email = email
    
    code = ""
    for i in range(6):
            code += str(random.randint(1,9))
    email_nums[email] = code
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Код подтверждения"
    body = code
    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    
    return "OK"


@application.route("/download_file/<int:user_id_1>/<int:user_id_2>/<string:token>/<filename>")
def send_message_fileq_route(user_id_1, user_id_2, token, filename):
    token_states = chek_token_db(user_id_1, token)
    if token_states == 'Токен_неверен':
             return jsonify(token_states)
    elif token_states == 'Токен_подтверждён':
        chat_id = take_one_chat_id(user_id_1, user_id_2)
        print(filename)
        folder = f"folder_{chat_id}"
  

        return send_from_directory(os.path.join(application.root_path, 'static', 'files', folder), filename, as_attachment=True)
     
@application.route("/send_message/<int:user_id_1>/<int:user_id_2>/<int:user_id>/<string:token>", methods=['POST'])
def send_message_route(user_id_1, user_id_2, user_id, token):
    user_id_1 = int(user_id_1)
    user_id_2 = int(user_id_2)
    token_states = chek_token_db(user_id_1, token)
    if token_states == 'Токен_неверен':
             return jsonify(token_states)
    elif token_states == 'Токен_подтверждён':
        chat_id = take_one_chat_id(user_id_1, user_id_2)
        data_json = request.form.get('data')
        data = json.loads(data_json)
        if data['type'] == 'text':
            send_message(user_id, data['text_message'], chat_id, data['type'])
        elif data['type'] == 'file':
            files_names = save_file(request.files.getlist('files'), user_id_1, chat_id)
            files_names_bd = '%'.join(files_names)
            send_message(user_id, files_names_bd, chat_id, 'file')
    return "Верно"






# Бэк функция
# Поиск пользователя, принимает email и user_id ищущего
# Возвращает информацию о юзере по email
@application.route("/find_user/<string:email>/<int:user_id>")
def find_user(email, user_id):

        user_fr_db = find_user_db(email, "from_find_user")

        if user_fr_db != False and user_fr_db != None and user_fr_db[0] != user_id:
            user = {
                'user_id': user_fr_db[0], 
                'first_name': user_fr_db[1], 
                'last_name': user_fr_db[2]
            }
        elif user_fr_db[0] == user_id:
             user = "Чат с самим собой в разработке"
        else:
             user = "Такой пользователь не зарегестирован"
        return  jsonify(user)
        

# Бэк функция
# Принимает id двух пользователей и максимальное сообщение
# Возвращает нужен ли апдейт
@application.route("/chat_chek_update/<int:user_id_1>/<int:user_id_2>/<int:message_id_MAX>")
def chat_chek_page_update(user_id_1, user_id_2, message_id_MAX):
    chat_id = take_one_chat_id(user_id_1, user_id_2)
   
    if chat_id == None:
         create_chat(user_id_1, user_id_2)
    chat_id = take_one_chat_id(user_id_1, user_id_2)
    resul_update = chek_updates_message(chat_id, message_id_MAX)
   
    return jsonify(resul_update)


# Бэк функция
# Принимает id двух юзеров
# Возвращает историю чата
@application.route("/chat_update/<int:user_id_1>/<int:user_id_2>/<string:token>")
def chat_page_update(user_id_1, user_id_2, token):
  
    token_states = chek_token_db(user_id_1, token)
    if token_states == 'Токен_неверен':
             return jsonify(token_states)
    elif token_states == 'Токен_подтверждён':
        chek_create_chat(user_id_1, user_id_2)
        chat_id = take_one_chat_id(user_id_1, user_id_2)
        if chat_id == None:
            create_chat(user_id_1, user_id_2)
        chat_id = take_one_chat_id(user_id_1, user_id_2)
        chat = load_one_chat(chat_id)
        i = 0
        if chat != None:
            while i != len(chat):        
                chat[i] = {
                    'user_id': chat[i][0],
                    'message_id': chat[i][1],
                    'type': chat[i][2],
                    'message_text': chat[i][3],
                    'message_date': str(chat[i][4]),
                    'message_time': str(chat[i][5])
                }
                i += 1
        else:
            chat = "Начните переписку"
        
        return jsonify(chat)
    else:
         return jsonify("Произошла ошибка. Код ошибки 6")


# Фронт функция
# Принимает user_id
# Возвращает страницу с чатами
@application.route("/main_page/<int:user_id>")
def main_page(user_id):
    return render_template('main_page.html', user_id=user_id)

@application.route("/main_page")
def main_page_without_user_id():
    return render_template('main_page.html')




# Бэк функция
# Принимает user_id_2
# Возвращает информацию о нём
@application.route("/load_user_info_chat/<int:user_id_2>")
def find_info_user_id_2(user_id_2):
    user_fr_db = find_info_user_id_2_db(user_id_2)
    if user_fr_db != False and user_fr_db != None:
            user = {
                'user_id': user_fr_db[0], 
                'first_name': user_fr_db[1], 
                'last_name': user_fr_db[2],
                'email': user_fr_db[3]
            }
  
    return jsonify(user)


# Бэк функция
# Принимает user_id и  token
# Возвращает прошёл ли токен проверку
@application.route("/main_page/token/<int:user_id>/<string:token>")
def chek_token(user_id, token):
    token_states = chek_token_db(user_id, token)
    return jsonify(token_states)     
   




# Бэк функция
# Принимает user_id и число чатов
# Возвращает есть обновления или нет
@application.route("/main_page_chek_update/<int:user_id>/<int:chats_MAX>")
def main_page_chek_update(user_id, chats_MAX):
    result_chek = load_len_user_chats(user_id, chats_MAX)
    return jsonify(result_chek)



# Бэк функция
# Принимает user_id
# Возвращает массивом все чаты юзера
@application.route("/main_page_update/<int:user_id>/<string:token>")
def main_page_update(user_id, token):
    token_states = chek_token_db(user_id, token)
    if token_states == 'Токен_неверен':
             return jsonify(token_states)
    elif token_states == 'Токен_подтверждён':
        chats = load_chats_id(user_id)
        i = 0
        while i != len(chats):
            if chats[i][1] == user_id:
                chats[i] = [chats[i][0], chats[i][2]]
            elif chats[i][2] == user_id:
                chats[i] = [chats[i][0], chats[i][1]]
            user = find_user_db_from_user_id(chats[i][1])
            last_message = load_last_mesasage(chats[i][0])
            chats[i] = {
                'chat_id':chats[i][0],
                'user_id':chats[i][1],
                'first_name':user[1],
                'last_name':user[2],
                'avatar':'null',
                'last_mes':last_message
            }
            i += 1
        
        return jsonify(chats)
    else:
         return jsonify("Произошла ошибка. Код ошибки 7")
    

if __name__ == "__main__":
       application.run(host="0.0.0.0", debug=False)