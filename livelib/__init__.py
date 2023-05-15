from .urlparser import Urlparser
from .parser import Parser, ParserFromHTML, ParserForDB, ParserForCSV, BookDataFormatter, ParserForXLSX
from .webconnection import WebConnection, SimpleWeb, WebWithCache
from .reader import Reader
from .dbconnection import DBConnection,SQLite3Connection
from .export import Export, CSVExport, XLSXExport
from .config import Config
import logging

logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a', format="%(asctime)s %(levelname)s %(message)s")

# @todo написать __doc__ для модуля