import os.path
from dataclasses import dataclass
from environs import Env

"""
Модуль для организации конфигурационных данных. 
Пример конфигурационного файла .env :
    ENCODING = utf-8
    
    SITE = http://www.livelib.ru
    
    CACHE_FOLDER = cache
    
    BS_FEATURES = lxml
    
    SQLITE_DB = db/main.db
    
    XLSX_FOLDER = export/xlsx
"""

@dataclass
class WebConnectionConfig:
    """
    Класс для хранения конфигурации веб-соединений.
    """
    site: str         # Адрес сайта по умолчанию формата http://www.livelib.ru
    cache_folder: str # папка для хранения кешированных страниц

@dataclass
class BSParserConfig:
    """
    Класс для хранения конфигурации парсера BeautifulSoup.
    """
    features: str # Способ парсинга BeautifulSoup. Рекоммендуется 'lxml'

@dataclass
class DBConfig:
    """
    Класс для хранения конфигурации базы данных.
    """
    sqlite_db: str # основная база данных в sqlite3

@dataclass
class XLSXConfig:
    """
    Класс для хранения конфигурации экспорта в xslx.
    """
    folder: str # папка для загрузки создаваемых файлов

@dataclass
class ExportConfig:
    """
    Класс для хранения конфигураций экспорта.
    """
    xlsx: XLSXConfig # класс хранения данных для экспорта в xlsx

@dataclass
class Config:
    web_connection: WebConnectionConfig
    bs_parser: BSParserConfig
    encoding: str
    db_config: DBConfig
    export: ExportConfig

    def __init__(self, path):
        env: Env = Env()
        if os.path.isfile(path):
            env.read_env(path,override=True)
            self.encoding = env('ENCODING')
            self.web_connection = WebConnectionConfig(site=env('SITE'), cache_folder=env('CACHE_FOLDER'))
            self.bs_parser = BSParserConfig(features=env('BS_FEATURES'))
            self.db_config = DBConfig(sqlite_db=env("SQLITE_DB"))
            self.export = ExportConfig(xlsx=XLSXConfig(folder=env('XLSX_FOLDER')))
        else:
            raise Exception(f'Can not read configuration from {path} file!')
