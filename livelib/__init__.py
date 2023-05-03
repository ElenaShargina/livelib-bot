from .urlparser import Urlparser
from .connection import Connection, SimpleWeb, WebWithCache
from .bsparser import BSParser
from .reader import Reader
import logging

logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a', format="%(asctime)s %(levelname)s %(message)s")

# @todo написать __doc__ для модуля