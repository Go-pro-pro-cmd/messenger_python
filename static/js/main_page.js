`use strict`;
const chat_none = document.getElementById('chat_none');
const chat_user = document.getElementById('chat_user');
const chats_container = document.getElementById('chats_container');
const header_cklic = document.getElementById('for_email');
const send_mes_inp_file = document.getElementById('user_file');
const header = document.getElementById('header');
const send_mes_btn = document.getElementById('send_mes_but');
const send_mes_input = document.getElementById('send_mes_inp');
const messages_container = document.getElementById('messages_container');

let first_name = localStorage.getItem('first_name');
let last_name = localStorage.getItem('last_name');
let email = localStorage.getItem('email');
let user_id = localStorage.getItem('user_id');
let token = localStorage.getItem('token');
let user_id_1 = user_id;
let user_id_2 = null;

sessionStorage.setItem('chats_MAX', 0);
send_mes_input.value = '';
send_mes_inp_file.value = '';
send_mes_inp_file.textConten = '';

function chek_token() {
    let states_token
    fetch(`/main_page/token/${user_id}/${token}`)
        .then(response => {
            if (!response.ok) {
                states_token = false;
            }
            return response.json();
        })
        .then(data => {
            if (data == 'Токен_подтверждён') {
                return null;
            } else if (data == 'Токен_неверен') {
                document.body.remove();
                alert('Ваши данные не сходятся')
                window.open('/');
            } else if (states_token == false) {
                alert('Ошибка проверки подлинности аккаунта _');
                document.body.remove();
                window.open('/');
            }
            else {
                alert('Ошибка проверки подлинности аккаунта');
                document.body.remove();
                window.open('/');

            }
        })
};
chek_token();

if (user_id_1 == user_id || user_id_2 == user_id) { }
else {
    alert("У вас нет доступа к данному чат!!!");
    document.body.innerHTML = "<h1>Доступ к данному чату ограничен по одной из причин</h1><ul><li><h3>Вы не являетесь участником данной переписки</h3></li><li><h3>Произошла ошибка на стороне сервера</h3></li></ul>"
};

function load_user_info() {
    fetch(`/load_user_info_chat/${user_id_2}`)
        .then(response => {
            if (!response.ok) {
                console.log("Произошла ошибка при проверке обновлений");
            };
            return response.json();
        })
        .then(data => {
            header.textContent = "Чат: " + data['first_name'] + " " + data['last_name'];
            header_cklic.innerHTML = ` <b>Email:</b>  ${data['email']}
                                       <br><b>Id:</b> ${data['user_id']}`;
        })
};

function send_message() {
    let send_message_text = send_mes_input.value;
    let type_message;
    let files = send_mes_inp_file.files[0] || null;
    if (files != null) {
        files = send_mes_inp_file.files;
    } else {
        files = null
    }
    send_mes_input.value = '';
    send_mes_inp_file.files = null;
    let formData = new FormData();
    if (files == null && send_message_text != '') {
        type_message = 'text';
        formData.append('data', JSON.stringify({
            'type': type_message,
            'text_message': send_message_text
        }))
    } else if (files != null && send_message_text == '') {
        type_message = 'file';
        formData.append('data', JSON.stringify({ 'type': type_message }))
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
    } else if (files != null && send_message_text != '') {
        type_message = 'file';
        formData.append('data', JSON.stringify({
            'type': type_message,
            'text_message': send_message_text
        }));
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        };
    } else {
        return 'Нет данных'
    }
    if (type_message == 'text' || type_message == 'text_file') {
        document.getElementById(`chat_last_mes_${user_id_2}`).textContent = send_message_text;
    };
    fetch(`/send_message/${user_id_1}/${user_id_2}/${user_id}/${token}`, {
        method: 'POST',
        body: formData
    });
};

// Подгружает сообщения
function chat_update() {
    fetch(`/chat_update/${user_id_1}/${user_id_2}/${token}`)
        .then(response => {
            if (!response.ok) {
                alert("Произошла ошибка, попробуйте снова")
            }
            return response.json();
        })
        .then(data => {
            if (data == 'Токен_неверен') {
                remove.body();
                alert('Ошибка синхронизации данных')
            } else {
                let message;
                let message_text;
                let message_file;
                let message_time;
                let message_date;
                let time_form;
                let files;
                if (data == "Новых данных нет") {
                    return "Сообщений нет"
                } else if (data != "Начните переписку") {
                    let i = 0;
                    let if2;
                    const messages_container_between = document.createElement('div');
                    messages_container_between.classList.add('messages_container_between');
                    while (i < data.length) {
                        time_form = data[i]['message_time'];
                        time_form = time_form.split(':');
                        time_form = time_form[0] + ':' + time_form[1]

                        message = document.createElement('div');
                        message.classList.add('message');
                        message.setAttribute('id', (data[i]['message_id']));
                        message.classList.add(data[i]['user_id']);
                        message.classList.add(data[i]['type']);
                        if (data[i]['user_id'] == user_id) {
                            message.classList.add('me_mes');
                        } else {
                            message.classList.add('no_me_mes');
                        }
                        message.setAttribute('title', data[i]['message_date'] + " " + data[i]['message_time'])

                        if (data[i]['type'] == 'text') {
                            message_text = document.createElement('div');
                            message_text.classList.add('message_text');
                            message_text.textContent = data[i]['message_text'];
                        } else if (data[i]['type'] == 'file') {
                            message_text = document.createElement('div')
                            if2 = 0;
                            files = data[i]['message_text'];
                            message_text.classList.add('message_text');
                            files = files.split('%');

                            while (if2 < files.length) {
                                message_file = document.createElement('a');
                                message_file.textContent = `Файл ${if2} `;
                                message_file.classList.add('file_href');
                                message_file.setAttribute('href', `/download_file/${user_id_1}/${user_id_2}/${token}/${files[if2]}`);
                                message_file.setAttribute('target', "_blank")
                                message_text.append(message_file);
                                if2++;
                            }
                        }
                        if (data[i]['user_id'] == user_id) {
                            message_text.classList.add('me_mes_txt');
                        } else {
                            message_text.classList.add('no_me_mes_txt');
                        }
                        message.append(message_text);

                        message_time = document.createElement('div');
                        message_time.classList.add('message_time');
                        message_time.innerHTML = time_form;
                        message.append(message_time);

                        i += 1;
                        messages_container_between.append(message);
                    };
                    messages_container.innerHTML = ''
                    messages_container.append(messages_container_between);
                    sessionStorage.setItem(`message_id_MAX_${user_id_1}_${user_id_2}`, data[data.length - 1]['message_id']);
                    //  document.getElementById(`chat_last_mes_${user_id_2}`).textContent = data[i--]['message_text'];
                    document.getElementById(data[data.length - 1]['message_id']).scrollIntoView({ behavior: 'smooth' });
                } else {
                    return
                }
            }
        })
};

//Проверяет на наличие обновлений 
// При наличии запускает функцию load_messages()
function chat_chek_update() {
    let message_id_MAX = sessionStorage.getItem(`message_id_MAX_${user_id_1}_${user_id_2}`);
    if (message_id_MAX == null) {
        message_id_MAX = 0
    };
    fetch(`/chat_chek_update/${user_id_1}/${user_id_2}/${message_id_MAX}`)
        .then(response => {
            if (!response.ok) {
                console.log("Произошла ошибка при проверке обновлений");
            };
            return response.json();
        })
        .then(data => {
            if (data == 'Обновлений нет') {
                return
            } else if (data == 'Обновления есть') {
                load_messages();
            }
        })
};

document.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        send_message();
        event.preventDefault();

    }
});

// Ищет user  по email
function find_user() {
    const email_html = document.getElementById('find_user_email');
    let email = email_html.value
    fetch(`/find_user/${email}/${user_id}`)
        .then(response => {
            if (!response.ok) {
                alert("Произошла ошибка , попробуйте снова. Код ошибки 1")

            }
            return response.json();
        })
        .then(data => {
            if (data == "Такой пользователь не зарегестирован") {
                alert(data);
                return;
            } else if (data == "Чат с самим собой в разработке") {
                alert(data);
                return;
            };
            let chat;
            let chat_text;
            let chat_avatar;
            let chat_last_mes;

            chat = document.createElement('button');
            chat.classList.add('chat');
            chat.setAttribute('id', 'chat_' + (data['user_id']));
            chat.setAttribute('onclick', `create_chat(${data['user_id']})`)

            chat_text = document.createElement('div');
            chat_text.textContent = data['first_name'] + ' ' + data['last_name'];
            chat_text.classList.add('chat_text');
            chat.append(chat_text);

            chat_last_mes = document.createElement('div');
            chat_last_mes.textContent = data['last_mes'];
            chat_last_mes.setAttribute('id', 'chat_last_mes_' + (data['user_id']));
            chat_last_mes.classList.add('chat_last_mes');
            chat.append(chat_last_mes)

            // Сделать подгрузку аватарки и её хранение
            chat_avatar = document.createElement('img');
            chat_avatar.classList.add('chat_avatar');
            chat.append(chat_avatar);

            chats_container.append(chat);

        })
}

// Подгружает чаты
function load_chats() {
    fetch(`/main_page_update/${user_id}/${token}`)
        .then(response => {
            if (!response.ok) {
                alert("Произошла ошибка, попробуйте снова. Код ошибки 2")
            }
            return response.json();
        })
        .then(data => {
            if (data == 'Токен_неверен') {
                remove.body();
                alert('Ошибка синхронизации данных')
            } else {
                if (data == "Новых данных нет") {
                    return "Сообщений нет"
                } else if (data != "Начните общение") {
                    let i = 0;
                    chats_container.innerHTML = ''
                    let chat;
                    let chat_text;
                    let chat_avatar;
                    let chat_last_mes;
                    while (i < data.length) {
                        chat = document.createElement('button');
                        chat.classList.add('chat');
                        chat.setAttribute('id', 'chat_' + (data[i]['user_id']));
                        chat.setAttribute('onclick', `create_chat(${data[i]['user_id']})`)

                        chat_text = document.createElement('div');
                        chat_text.textContent = data[i]['first_name'] + ' ' + data[i]['last_name'];
                        chat_text.classList.add('chat_text');
                        chat.append(chat_text);

                        chat_last_mes = document.createElement('div');
                        chat_last_mes.textContent = data[i]['last_mes'];
                        chat_last_mes.setAttribute('id', 'chat_last_mes_' + (data[i]['user_id']));
                        chat_last_mes.classList.add('chat_last_mes');
                        chat.append(chat_last_mes);

                        // Сделать подгрузку аватарки и её хранение
                        chat_avatar = document.createElement('img');
                        chat_avatar.classList.add('chat_avatar');
                        chat.append(chat_avatar);

                        chats_container.append(chat);
                        i += 1;

                    };
                    sessionStorage.setItem('chats_MAX', i)
                } else {
                    return
                }
            }
        })
};
load_chats();

function chek_update_main_page() {
    let chats_MAX = sessionStorage.getItem('chats_MAX');
    if (chats_MAX == null) {
        chats_MAX = 0
    };
    fetch(`/main_page_chek_update/${user_id}/${chats_MAX}`)
        .then(response => {
            if (!response.ok) {
                console.log("Произошла ошибка при проверке обновлений");
            };
            return response.json();
        })
        .then(data => {
            if (data == 'Обновлений нет') {
                return
            } else if (data == 'Обновления есть') {
                load_chats();
            }
        })
};

function create_chat(us_2) {
    user_id_2 = us_2;
    chat_none.style.display = 'none';
    chat_user.style.display = 'block';
    chat_chek_update();
    load_user_info();
    setTimeout(() => { chat_update() }, 3000);

    setInterval(() =>
        chek_update(), 1000);
}

setInterval(() =>
    chek_update_main_page(), 5000);



