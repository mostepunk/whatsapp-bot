import base64
import logging
import os
from configparser import ConfigParser
from objects.user_language import UserLanguage
from objects.database import Database

speaker = UserLanguage()

def config_get_param(section, param):
    """Извлекает из файла всю необходимую мне инфу
        из файла config.ini
        быть аккуратным при изменении этого метода
        этот метод продублирован в
            objects/db.py
            objects/user_language.py
    """
    config_file = "config.ini"
    conf = ConfigParser()
    conf.read(config_file)
    value = conf.get(section, param)
    return value

db_auth_users = Database("config.ini", "mysql", config_get_param("tables", "users"))

def check_text_message(message, user_phone):
    """Обработка текстовых сообщений
       Принимает текстовое сообщение, обрабатывает его
       и возвращает ответ из английского или русского словаря (ru/en.ini файл)
       ---------------
       Методы:
          * help        - Помощь для взаимодействия
          * add_user    - Добавить пользователя в БД авторизоваанных пользователей
             - Чтобы добавить нового пользователя надо отправить:
                  add_user <password_admin> 7xxxxxxxxxx
             - password_admin - переменная в файле config.ini
          * ru/en       - Сменить язык для общения с пользователем
          * else        - Стандартный ответ в любой непонятной ситуации
       ---------------
    """
    message = message.lower()
    logging.info(
        'Started check_text_message\nUser_ID= {}\ntext - {}'
        .format(user_phone, message)
        )

    if message == 'help':
        new_msg = speaker.get_message(user_phone, "bot_message", "help")

    elif message.startswith('add_user'):
        message_list = message.split()
        logging.info(
            'User_ID={} want to add {} to AuthorizedUsers'
            .format(user_phone, message_list[1])
            )

        if message_list[2] == config_get_param("bot", "passwd_admin"):
            logging.info(
                'add_user: admin password correct'
                )
            db_auth_users.add_user_to_db(int(message_list[1]))

            return_list = []
            new_msg = speaker.get_message(
                user_phone, "bot_message", "successful_add")\
                .format(message_list[1])

            new_msg2 = speaker.get_message(
                user_phone, "bot_message", "successful_registration")\
                .format(message_list[1])

            return_list.append(new_msg)
            return_list.append(new_msg2)
            return_list.append(message_list[1])

            logging.info(
                "User_ID = {} added to 'AuthorizedUsers' new User with ID = {}"
                .format(user_phone, message_list[1]))
            return return_list

        else:
            new_msg = speaker.get_message(user_phone, "bot_message", "standart")
            logging.info(
                "User_ID = {} add_user: password incorrect"
                .format(user_phone)
                )

    elif message == 'ru':
        db_auth_users.add_user_language(user_phone, "ru")
        new_msg = speaker.get_message(user_phone, "bot_message", "lang")
        logging.info(
            'User {} changed language on RU'
            .format(user_phone))

    elif message == 'en':
        db_auth_users.add_user_language(user_phone, "en")
        new_msg = speaker.get_message(user_phone, "bot_message", "lang")
        logging.info(
            'User {} changed language on EN'
            .format(user_phone)
            )

    else:
        new_msg = speaker.get_message(user_phone, "bot_message", "start")

    logging.info(
        'User_ID - {} Soon wil get a message \n{}'
        .format(user_phone, new_msg))
    return new_msg

def user_info(sms):
    """возвращает user_phone и language_code"""
    user_phone = sms.getFrom()[:11]

    if user_phone[0] == '7':
        language_code = 'ru'
    else:
        language_code = 'en'

    logging.info(
        'Got user_phone - {} and user_language - {}'
        .format(user_phone, language_code)
        )

    return user_phone, language_code

def user_directory(phone):
    storage_dir = (
        config_get_param("bot", "path") +
        "userID_" + str(phone))
    if os.path.exists(storage_dir) is False:
        os.mkdir(storage_dir)
        logging.info(
            'Created directory %s',
            storage_dir)
        return storage_dir
