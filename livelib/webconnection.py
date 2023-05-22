import _io
import bs4
import requests
import os
import re
import logging
from typing import List
from .parser import ParserFromHTML
import time, random
from .config import Config


class WebConnection:
    """
    Абстрактный класс соединения, позволяющий получить страницы сайта.
    :param site: адрес сайта формата "http://www.livelib.ru",
        defaults to  'http://www.livelib.ru'
    :type site: str
    :param bs_parser: тип парсера BeautifulSoup, который будет применяться к страницам,
        defaults to 'lxml'
    :type bs_parser: str
    :param encoding: кодировка сайта
        defaults to 'utf-8'
    :type encoding: str
    """

    def get_page_status(self, url: str) -> int:
        """
        Возвращает статус запроса к странице.
        :param url: адрес страницы.
        :return: статус запроса к странице, 0 в случае её недоступности.
        :rtype: int
        """
        # @todo нужно ли для simpleweb?
        pass

    def get_page_text(self, url: str) -> str:
        """
        Возвращает текст страницы, либо генерирует исключение
        :param url: адрес страницы
        :return: текст страницы
        :rtype: str
        """
        pass

    def _get_page_bs(self, url: str) -> bs4.BeautifulSoup:
        """
        Возвращает объект BeautifulSoup, сгенерированный из страницы по заданному адресу, либо генерирует исключение.
        :param url: адрес страницы
        :raises Exception: если невозможно получить объект BSoup по заданному адресу
        :return: объект BeautifulSoup из страницы по адресу
        :rtype: bs4.BeautifulSoup
        """
        try:
            result = bs4.BeautifulSoup(self.get_page_text(url), features=self.bs_parser)
        except Exception:
            logging.exception(f'Can not get BS object from {url}', exc_info=True)
            result = None
        else:
            return result

    def get_page_bs(self, url: str, parser=ParserFromHTML) -> bs4.BeautifulSoup or bool:
        """
        Возвращает объект BeautifulSoup из этой страницы.
        Возвращает False,   если сайт не существует,
                            если livelib по данному адресу выдает 404,
                            если livelib выдает капчу для защиты от роботов.
        :param url: адрес страницы
        :param parser: класс парсера для обработки страниц
            defaults to Parser
        :raises Exception: если невозможно получить объект BSoup по заданному адресу
        :return: объект BeautifulSoup из страницы по адресу
        :rtype: bs4.BeautifulSoup
        """
        try:
            result = bs4.BeautifulSoup(self.get_page_text(url), features=self.bs_parser)
        except Exception:
            logging.exception(f'Can not get BS object from {url}', exc_info=True)
            return False
        else:
            # проверяем на 404
            if parser.check_404(result):
                logging.warning(f'Page at {url} is 404!')
                return False
            elif parser.check_captcha(result):
                logging.warning(f'Page at {url} is captcha!')
                return False
            else:
                return result


class SimpleWeb(WebConnection):
    """
    Класс соединения, получающий страницы сайта только из сети напрямую.
    Так как сайт Livelib медленный и не поддерживает много запросов,
    то во всех случаях пользоваться этим классом не оптимально.
    :param site: адрес сайта формата "http://www.livelib.ru",
        defaults to  'http://www.livelib.ru'
    :type site: str
    :param bs_parser: тип парсера BeautifulSoup, который будет применяться к страницам,
        defaults to 'lxml'
    :type bs_parser: str
    :param encoding: кодировка сайта
        defaults to 'utf-8'
    :type encoding: str
    :param: random_sleep перед запросом страницы засыпание на случайное количество секунд, нужно для обхода блокировок Livelib
        default to False
    :type random_sleep: bool
    """

    def __init__(self, config: Config, random_sleep=False):
        self.site = config.web_connection.site
        self.bs_parser = config.bs_parser.features
        self.encoding = config.encoding
        self.random_sleep = random_sleep

    def do_random_sleep(self):
        time_to_sleep = random.randint(90, 120)
        print(f'Sleep for {time_to_sleep} seconds.')
        time.sleep(time_to_sleep)

    def _get_page(self, url: str) -> requests.Response:
        """
        возвращает объект Response по запросу на заданный адрес, либо генерирует исключение.
        :param url: адрес страницы
        :raises Exception: если невозможно получить страницу
        :rtype: requests.Response
        :return: объект Response по запросу на заданный адрес
        """
        logging.debug(f'Making request to {url}')
        if self.random_sleep:
            logging.debug('Random sleep.')
            self.do_random_sleep()
        # если начало url - не ссылка на сайт, то добавляем
        if url[0] == '/':
            url = self.site + url
            logging.debug(f'Add site prefix to url')
        try:
            headers = requests.utils.default_headers()
            headers.update(
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                }
            )
            result = requests.get(url, headers=headers)
            result.encoding = self.encoding
            return result
        except Exception:
            logging.exception(f'Can not open this page!', exc_info=True)
            raise

    def get_page_status(self, url: str) -> int:
        """
        Возвращает статус запроса к странице.
        :param url: адрес страницы
        :return: статус запроса к странице, 0 в случае её недоступности.
        :rtype: int
        """
        try:
            return self._get_page(url).status_code
        except Exception:
            return 0

    def get_page_text(self, url: str) -> str:
        """
        Возвращает текст страницы по заданному адресу.
        :param url: адрес страницы
        :type url: str
        :raises Exception: если невозможно получить текст страницы
        :return: текст страницы
        :rtype: str
        """
        try:
            page = self._get_page(url)
        except Exception:
            logging.exception(f'Can not get text from page! {url}', exc_info=True)
            raise
        else:
            return page.text


class WebWithCache(WebConnection):
    """
    Класс соединения, позволяющий получить страницы сайта из локального кеша или, если их там нет, из сети.
    Так как сайт Livelib медленный и не поддерживает много запросов, то этот вид соединения экономит время.
    :param site: адрес сайта формата "http://www.livelib.ru",
        defaults to  'http://www.livelib.ru'
    :type site: str
    :param bs_parser: тип парсера BeautifulSoup, который будет применяться к страницам,
        defaults to 'lxml'
    :type bs_parser: str
    :param encoding: кодировка сайта
        defaults to 'utf-8'
    :type encoding: str
    :param: random_sleep перед запросом страницы с помощью SimpleWeb засыпание на случайное количество секунд, нужно для обхода блокировок Livelib
        default to False
    :type random_sleep: bool
    :param default_file_name: название файлов для сохранения в кеше по умолчанию
        defaults to 'index'
    :type default_file_name: str
    :param default_file_extension: расширение файлов для сохранения в кеше по умолчанию
        defaults to '.html'
    :type default_file_extension: str
    :param folder: папка для хранения кеша
        defaults to 'cache'
    :type folder: str

    """
    default_file_name = 'index'
    default_file_extension = '.html'

    def __init__(self, config: Config, random_sleep=False):
        self.config = config
        self.site = config.web_connection.site
        self.bs_parser = config.bs_parser.features
        self.encoding = config.encoding
        self.folder = config.web_connection.cache_folder
        self.random_sleep = random_sleep

    def _parse_url_in_filepath_and_filename(self, url: str) -> list[str, str]:
        """
        Подготовка для сохранения страницы в кеше: разбивает адрес страницы на директории и название файла.
        Например, http://www.livelib.ru/reader/qwerty/books -> ['/cache/reader/qwerty/','books.html']
        или http://www.livelib.ru/reader/qwerty/books/1 -> ['/cache/reader/qwerty/books/','1.html']
        :param url:
        :type url:
        :return: адрес пути к файлу кеша и название файла
        :rtype: List[str,str]
        """
        # понижаем все в нижний регистр
        url = url.lower()
        # убираем префикс с именем сайта
        url = url.removeprefix(self.site)
        r_ext = re.compile(r'\.[^\.]+$')
        r_file_name = re.compile(r'[^/]+$')
        # проверим на наличие расширения файла и уберем его, если оно есть
        if re.search(r_ext, url):
            url = url.removesuffix(re.search(r_ext, url).group())
        # вытащим название файла (после последнего слеша), перед ним будет путь к файлу
        # или поставим значение по умолчанию для названия файла
        if re.search(r_file_name, url):
            file_name = re.search(r_file_name, url).group()
            path = url.removesuffix(file_name)
        else:
            path = url
            file_name = self.default_file_name
        # добавляем корневую папку
        path = self.folder + path
        # добавим расширение по умолчанию
        file_name = file_name + self.default_file_extension
        return [path, file_name]

    def _create_file(self, url: str, text: str = '') -> _io.TextIOWrapper:
        """
        Сохраняет файл с заданным содержимым в дереве папок, соответствующем адресу страницы, и возвращает этот файл.
        :param url: адрес страницы
        :type url: str
        :param text: содержимое страницы,
            defaults to ''
        :type text: str
        :return: объект файла с текстом или False, если не удалось сохранить файл.
        :rtype: _io.TextIOWrapper or False
        """
        path, file_name = self._parse_url_in_filepath_and_filename(url)
        # проверяем, существует ли файл
        # @todo а если файл существует и мы хотим его принудительно переписать?
        if not os.path.isfile(path + file_name):
            # создадим весь путь из папок до нужного файла
            dirs = path.split('/')
            path_dir = ''
            for i in range(len(dirs)):
                path_dir = '/'.join(dirs[:i + 1])
                logging.debug(f'Dir {path_dir} is found? {os.path.isdir(path_dir)}')
                if not os.path.isdir(path_dir):
                    logging.debug(f'Create dir {path_dir}')
                    os.mkdir(path_dir)
            # создаем файл
            try:
                my_file = open(path + file_name, mode='x', encoding=self.encoding)
                my_file.write(text)
                logging.debug(f'Create file {my_file} ')
                my_file.close()
            except Exception:
                logging.exception(f'Can not open file for offline connection at {path}{file_name} .', exc_info=True)
                return False
        # открываем вновь созданный или имеющийся файл
        try:
            logging.debug(f'Already have {path + file_name}')
            f = open(path + file_name, mode='r', encoding=self.encoding)
            return f
        except Exception:
            logging.exception(f'Can not open file for offline connection at {path}{file_name} .', exc_info=True)
            return False

    def _get_page(self, url: str) -> str:
        """
           Возвращает текст страницы по заданному адресу, добывая его из кеша или из сети, либо генерирует исключение.
           :param url: адрес страницы
           :raises Exception: если невозможно получить страницу.
           :rtype: requests.Response
           :return: объект Response по запросу на заданный адрес
           """
        path, file_name = self._parse_url_in_filepath_and_filename(url)
        # если страница уже есть в кеше, то возвращаем текст из файла
        if os.path.isfile(path + file_name):
            # print(f'Page {url} is in dump.')
            logging.debug(f'Page {url} is in dump.')
            try:
                f = open(path + file_name, mode='r', encoding=self.encoding)
                result = f.read()
                f.close()
                return result
            except Exception as exc:
                logging.exception(f'Can not load file {path}{file_name} ', exc_info=True)
                raise
        # если нет, вызываем ее через simpleweb и сохраняем в кеше
        else:
            web = SimpleWeb(config=self.config,
                            random_sleep=self.random_sleep)
            web_text = web.get_page_text(url)
            if web_text:
                f = self._create_file(url, web_text)
                result = f.read()
                f.close()
                return result
            else:
                logging.exception(f'Can not get page at {url}', exc_info=True)
                raise

    def get_page_status(self, url: str) -> int:
        """
        Возвращает статус запроса к странице.
        :param url: адрес страницы
        :return: статус запроса к странице, 0 в случае её недоступности.
        :rtype: int
        """
        result = self._get_page(url)
        if len(result) > 0:
            return 200
        else:
            return 0
        return result

    def get_page_text(self, url: str) -> str:
        """
        Возвращает текст страницы по заданному адресу
        :param url: адрес страницы
        :type url: str
        :raises Exception: если невозможно получить текст страницы
        :return: текст страницы
        :rtype: str
        """
        result = self._get_page(url)
        return result
