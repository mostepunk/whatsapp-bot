# этот объект специально создан для user_languages.py
# чтобы не было перекрестного импорта, без него все падает
import time
import datetime
import re
import mysql.connector
import mysql.connector.pooling
import logging
from configparser import ConfigParser


def config_get_param(section, param):
    """ DUBLICATE
        извлекает из файла всю необходимую мне инфу
    """
    config_file = "config.ini"
    conf = ConfigParser()
    conf.read(config_file)
    value = conf.get(section, param)
    return value

class Database():
    def __init__(self, config_file, section, table):
        self.config_file = config_file
        self.section = section
        self.table = table
        self.db_config = self.read_dbconfig()
        self.connect()

    def read_dbconfig(self):
        """Читаем конфиг файл с инфой о БД"""
        parser = ConfigParser()
        parser.read(self.config_file)
        db = {}
        if parser.has_section(self.section):
            items = parser.items(self.section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception(
                "Section '{}' not found in the file '{}'"
                .format(self.section, self.config_file))
        return db

    def connect(self):
        while True:
            try:
                self.conn_pool = (
                    mysql.connector.pooling.MySQLConnectionPool(
                        pool_size=10, **self.db_config))

            except mysql.connector.errors.InterfaceError as exc:
                logging.error(exc)
                time.sleep(3)
            else:
                logging.info("Connected to DataBase")
                break

    def get_conn(self):
        while True:
            try:
                conn = self.conn_pool.get_connection()
                conn.autocommit = True
            except Exception as e:
                logging.exception(e)
                time.sleep(1)
            else:
                return conn

    def get_user_language(self, user_id):
        while True:
            cursor = None
            try:
                conn = self.get_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT language FROM {} WHERE user_id = {}" \
                               .format(self.table, user_id))
                row = cursor.fetchone()
                if row == None:  # по умолчанию ставим английский язык
                    lang = "en"
                else:
                    lang = row[0]

            except mysql.connector.errors.OperationalError as e:
                logging.error(e)
                self.connect()
            except mysql.connector.errors.InterfaceError as e:
                logging.exception(e)
                self.connect()
            except Exception as e:
                logging.exception(e)
            else:
                return lang
            finally:
                conn.close()
                if cursor:
                    cursor.close()

    # def __exit__(self, exc_type, exc_val, exc_tb):
        # conn.close()


