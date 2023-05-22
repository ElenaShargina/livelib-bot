from .parser import Parser, ParserFromHTML, ParserForDB, ParserForCSV, BookDataFormatter, ParserForXLSX
from .webconnection import WebConnection, SimpleWeb, WebWithCache
from .reader import Reader
from .dbconnection import DBConnection,SQLite3Connection
from .export import Export, XLSXExport
from .config import Config
import logging

logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a', format="%(asctime)s %(levelname)s %(message)s")

"""
Пакет livelib для парсинга данных с сайта livelib.ru.

В версии 1.0 :
 - забирает прочитанные указанным читателем книги 
 - экспортирует их в xlsx формате

Классы:
    Reader - основной класс
    Config - класс для загрузки конфигурации
    WebConnection - классы для соединения с веб
        SimpleWeb(WebConnection) - класс для соединения с веб напрямую
        WebWithCache(WebConnection) - класс для соединения с веб с кешированием данных
    DBConnection - классы для соединения с базой данных
        SQLite3Connection(DBConnection) - класс для соединения с базой данных sqlite3
    Export - классы для экспорта
        XLSXExport(Export) - класс для экспорта данных в формате xlsx
    Parser - классы для парсинга данных
        ParserFromHTML(Parser) - класс для парсинга страниц сайта в формате html
        ParserForDB(Parser) - класс для подготовки данных для сохранения в БД
        ParserForXLSX(Parser) - класс для подготовки данных для сохранения в XLSX
    DataFormatter - класс задания соответствий между свойствами свойств на сайте (парсинг HTML) 
                    и колонок в БД и XLSX
        BookDataFormatter(DataFormatter) - класс задания соответствий 
                                            между свойствами книг на сайте и колонок в БД и XLSX

"""