import logging
from logging.handlers import TimedRotatingFileHandler

__version__ = "3.2.3"
__author__ = "Tarek Galal"

logger = logging.getLogger(__name__)
# logger = logging.getLogger('MyYowsupLOGGER')

# create console handler and set level to debug

ch = logging.StreamHandler()

# ch2 =TimedRotatingFileHandler(
    # '/var/log/wabot.log',
    # when="midnight")
# ch2 = logging.FileHandler('/var/log/wabot.log')

ch.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter('%(levelname).1s %(asctime)s %(name)s - %(message)s')
formatter =logging.Formatter("%(asctime)s : %(filename)s[LINE:%(lineno)d] : %(levelname)s : %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# ch2.setFormatter(formatter)

# ch = logging.FileHandler('/var/log/server.log')
# add ch to logger
logger.addHandler(ch)
# logger.addHandler(ch2)

# logger.info('\n\n=== TEST === \n\n')
