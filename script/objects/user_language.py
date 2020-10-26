from configparser import ConfigParser
import logging
from objects.db import Database


def config_get_param(section, param):
    """ DUBLICATE
        извлекает из файла всю необходимую мне инфу
    """
    config_file = "config.ini"
    conf = ConfigParser()
    conf.read(config_file)
    value = conf.get(section, param)
    return value

db_auth_users = Database("config.ini", "mysql", config_get_param("tables", "users"))

class UserLanguage():
    def get_config_filename(self, language):
        config = language + ".ini"
        return config

    def get_message(self, user_id, section, param):
        value = ''
        try:
            lang_list = config_get_param("bot", "languages")
            user_lang = db_auth_users.get_user_language(user_id)
            # user_lang ='ru'

            if user_lang == None: # по умолчанию ставим английский язык
                user_lang = "en"

            else:
                if user_lang[0:2] in lang_list:
                    user_lang = user_lang[0:2]

                else:
                    user_lang = "en"

            logging.info("Language of User with ID = {} is '{}'".format(user_id, user_lang))
            config_file = self.get_config_filename(user_lang)

            conf = ConfigParser()
            conf.read(config_file)

            value = conf.get(section, param)
        except Exception as err:
            logging.exception(err)
        return value

    def get_message_unauthorized_users(self, user_id, section, param, user_lang):
        value = ''
        try:
            logging.info("User_ID = {} : language = {}".format(user_id, user_lang))
            lang_list = config_get_param("bot", "languages")
            if user_lang == None: # по умолчанию ставим английский язык
                user_lang = "en"
            else:
                if user_lang[0:2] in lang_list:
                    user_lang = user_lang[0:2]
                else:
                    user_lang = "en"
            config_file = self.get_config_filename(user_lang)
            conf = ConfigParser()
            conf.read(config_file)
            value = conf.get(section, param)
        except Exception as err:
            logging.exception(err)
        return value


