from dataclasses import dataclass
from environs import Env


@dataclass
class WebConnectionConfig:
    site: str         # Адрес сайта по умолчанию формата http://www.livelib.ru
    cache_folder: str # папка для хранения кешированных страниц

@dataclass
class BSParserConfig:
    features: str # Способ парсинга BeautifulSoup

@dataclass
class DBConfig:
    sqlite_db: str # основная база данных в sqlite3

@dataclass
class Config:
    web_connection: WebConnectionConfig
    bs_parser: BSParserConfig
    encoding:str

    def __init__(self, path):
        env: Env = Env()
        env.read_env(path)
        print('from config',path)
        self.encoding = env('ENCODING')
        self.web_connection = WebConnectionConfig(site=env('SITE'), cache_folder=env('CACHE_FOLDER'))
        self.bs_parser = BSParserConfig(features=env('BS_FEATURES'))
