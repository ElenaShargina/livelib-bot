from .urlparser import Urlparser
from .parser import Parser
from .connection import Connection, SimpleWeb, WebWithCache
from .reader import Reader
import logging

logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a', format="%(asctime)s %(levelname)s %(message)s")

# @todo написать __doc__ для модуля