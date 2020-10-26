from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock
import queue as Queue
import threading
import logging
import os
import sys
import time
import json
import requests

from yowsup.layers.protocol_messages.protocolentities.message_text \
    import TextMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities import *
from yowsup.layers.network.layer import YowNetworkLayer
from yowsup.layers.protocol_presence.protocolentities.presence_available \
    import AvailablePresenceProtocolEntity
from yowsup.layers.protocol_chatstate.protocolentities.chatstate_outgoing \
    import OutgoingChatstateProtocolEntity
from yowsup.common.tools import Jid
from yowsup.layers import YowLayerEvent, EventCallback

from objects import basic
from objects.database import Database
from objects.user_language import UserLanguage
from objects.wa_downloader import WADocumentDownloader
from objects.wa_uploader import WAUploader
from objects.wa_check_status import WebCheckingStatus
from objects.wa_link_downloader import LinkDownloader


SLEEP_TIME = 0.25
ROOT_PATH = '/usr/src/wabot/yowsup/'

class MainStrongFastSuperBot(YowInterfaceLayer):
    """Тело бота"""
    def __init__(self):
        super(MainStrongFastSuperBot, self).__init__()
        self.speaker = UserLanguage()
        self.db_auth_users = Database(
            "config.ini", "mysql",
            basic.config_get_param("tables", "users")
            )
        self.data_pool = ThreadPoolExecutor(20)
        self.text_pool = ThreadPoolExecutor(10)
        self.check_pool = ThreadPoolExecutor(20)
        self.locker = Lock()

    @ProtocolEntityCallback("message")
    def on_message(self, sms):
        """Обработчик всех входящих сообщений"""
        user_phone, language_code = basic.user_info(sms)
        # If user authorized: start messaging
        if self.db_auth_users.check_user(user_phone) is True:
            # chek if user has language in DB, if not: add language_code
            if self.db_auth_users.get_user_language(user_phone) is None:
                self.db_auth_users.add_user_language(user_phone, language_code)

            if sms.getType() == 'text':
                # if text, send to text_handler
                self.text_pool.submit(self.text_handler, sms)
                time.sleep(SLEEP_TIME)

            elif sms.getType() == 'media':
                self.data_pool.submit(self.document_worker, sms)
                time.sleep(SLEEP_TIME)

        else:
            # if not authorized, send standart msg
            text = (
                self.speaker.get_message_unauthorized_users(
                    user_phone, "bot_message", "unauthorized", language_code)
                .format(user_phone)
                )
            self.send_message(text, user_phone, sms)

    def text_handler(self, sms):
        """обработчик текстовых сообщений"""

        logging.info('text_handler started')
        user_phone, _ = basic.user_info(sms)

        text = basic.check_text_message(sms.getBody(), user_phone)

        if isinstance(text, str):
            self.send_message(text, user_phone, sms)

        elif isinstance(text, list):
            # если после обработчика вернулся список
            # прислыать админу смс, что пользователь добавлен
            # прислать пользователю "Добро пожаловать"
            to_admin = text[0]
            self.send_message(to_admin, user_phone, sms)

            to_user = text[1]
            self.send_message(to_user, text[2], sms)

    def document_worker(self, sms):
        """скачивает полученные медиа в папку
             downloaded_files/user_ID7xxxxxxx/
        """
        self.toLower(sms.ack())
        user_phone, _ = basic.user_info(sms)
        if int(sms.file_length) > int(
                basic.config_get_param("bot", "max_size_file")):

            logging.info(
                'User_ID = {} sent incorrect document\n\tLength - {}\n\tName - {}'
                .format(user_phone, sms.file_length, sms.filename)
                )

            text = self.speaker.get_message(
                user_phone, "bot_message", "large_file_size")
            self.send_message(text, user_phone, sms)

        else:
            logging.info(
                'User_ID = {} sent correct document, begin download'
                .format(user_phone))

            # start downloading...
            storage_dir = basic.user_directory(user_phone)
            downloader = WADocumentDownloader(storage_dir)

            # возвращает имя и путь файла, если нужна дальнейшая работа с ними
            # если фаайл прислан как документ, возвращает родное имя
            # если изображение имя - image и тд
            filepath, filename = downloader.run(sms)

    def send_message(self, text, phone, sms):
        """Метод отправки сообщений
           принимает текст для отправки
           номер телефона
           и объект смс(опционально) - TextMessageProtocolEntity
        """
        with self.locker:
            self.toLower(sms.ack())     # sms delivered (vv)
            self.toLower(AvailablePresenceProtocolEntity())
            self.toLower(
                OutgoingChatstateProtocolEntity(
                    OutgoingChatstateProtocolEntity.STATE_TYPING,
                    Jid.normalize(sms.getFrom(False)))) # typing...
        time.sleep(3)
        with self.locker:
            self.toLower(
                OutgoingChatstateProtocolEntity(
                    OutgoingChatstateProtocolEntity.STATE_PAUSED,
                    Jid.normalize(sms.getFrom(False)))) # typing OFF
            self.toLower(sms.ack(True)) # sms is read(blue vv)

            if phone.isdigit():
                phone += '@s.whatsapp.net'

            data = TextMessageProtocolEntity(text, to=phone)
            try:
                self.toLower(data)
                logging.info(
                    'User_ID={} received message - {}'
                    .format(phone, text)
                    )
            except Exception as err:
                logging.exception(
                    'ERROR in send_message User_ID={} : {}'.format(phone, err))

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        """Отправляет ответ на сервер Whatsapp, что сообщение доставлено
           без этого метода будет падать в ошибку
            Stream Error type: ack
            {'ack': None}
        """
        self.toLower(entity.ack())

    @ProtocolEntityCallback("event")
    def onEvent(self, layerEvent):
        alive_thread = Thread(target=self.aliver, args=(layerEvent,))
        logging.info("WhatsApp-Plugin : EVENT " + layerEvent.getName())

        if layerEvent.getName() == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            logging.info(
                "WhatsApp-Plugin : Disconnected reason: %s"%layerEvent.getArg("reason")
                )
            os._exit(os.EX_OK)

            if layerEvent.getArg("reason") == 'Connection Closed':
                time.sleep(2)
                logging.info("WhatsApp-Plugin : Issueing EVENT_STATE_CONNECT")

                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
            elif layerEvent.getArg("reason") == 'Ping Timeout':
                time.sleep(2)
                logging.info(
                    "WhatsApp-Plugin : Issueing EVENT_STATE_DISCONNECT")

                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))
                time.sleep(2)
                logging.info(
                    "WhatsApp-Plugin : Issueing EVENT_STATE_CONNECT")

                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

            elif layerEvent.getArg("reason") == 'Authentication Failure':
                time.sleep(2)
                logging.info("WhatsApp-Plugin : Issueing EVENT_STATE_CONNECT")

                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

            else:
                time.sleep(2)
                logging.info("WhatsApp-Plugin : Issueing EVENT_STATE_CONNECT")

                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

            os._exit(os.EX_OK)


        elif layerEvent.getName() == YowNetworkLayer.EVENT_STATE_CONNECTED:
            logging.info("WhatsApp-Plugin : Connected")
            alive_thread.start()

    @ProtocolEntityCallback("success")
    def onSuccess(self, layerEvent):
        """При успешном коннекте можно выполнять любые действия
           Я решил отправлять себе сообщение, чтобы понимать, сколько раз он презапускается
        """
        admin = '7xxxxxx@s.whatsapp.net'
        data = TextMessageProtocolEntity('Я родился', to=admin)
        self.toLower(data)


