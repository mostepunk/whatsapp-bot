import sys
import os
import time
from threading import Thread

from logging.handlers import TimedRotatingFileHandler
import logging
logging.basicConfig(
    format="%(asctime)s : %(filename)s : %(threadName)s_%(thread)d(%(funcName)s)[LINE:%(lineno)d] : %(levelname)s : %(message)s",
    level=logging.DEBUG,
    filename='/var/log/wabot.log',
    filemode='w')

from objects import basic
from objects.main_layer import MainStrongFastSuperBot
from objects.echo_layer import EchoLayer

from yowsup.stacks import  YowStackBuilder
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.axolotl.props import PROP_IDENTITY_AUTOTRUST



class YowsupEchoStack(object):
    def __init__(self):
        stackBuilder = YowStackBuilder()
        self.profile = os.environ['phone_number']

        self._stack = stackBuilder\
            .pushDefaultLayers()\
            .push(MainStrongFastSuperBot)\
            .build()

        self._stack.setProfile(self.profile)
        self._stack.setProp(PROP_IDENTITY_AUTOTRUST, True)

    def set_prop(self, key, val):
        self._stack.setProp(key, val)

    def start(self):
        logging.info("Staker good one")
        self._stack.broadcastEvent(
            YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        self._stack.loop(timeout=0.5, discrete=0.5)

if __name__ == "__main__":

    while True:
        try:
            y = YowsupEchoStack()
            y.start()
            logging.info('RESTART WABOT...')

        except KeyboardInterrupt:
            logging.info("The module was stopped")
        except Exception as err:
            logging.exception(
                "The module was failed {}".format(err))

