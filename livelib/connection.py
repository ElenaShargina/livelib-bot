import requests
import os
import re

class Connection:
    def __init__(self, site='http://www.livelib.ru', bs_parser='lxml', encoding='utf-8'):
        self.site = site
        self.bs_parser = bs_parser
        self.encoding = encoding

    def get_page(self,url):
        pass

    def get_page_status(self, url):
        pass

    def get_page_text(self, url):
        pass

class SimpleWeb(Connection):
    def get_page(self, url):
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
        except Exception as exc:
            print(f'Can not open this page! {exc}')
            return False

    def get_page_status(self, url):
        try:
            return self.get_page(url).status_code
        except Exception:
            return 0

    def get_page_text(self, url):
        try:
            return self.get_page(url).text
        except Exception:
            return None

class Offline(Connection):
    folder = 'offline'
    default_file_name = 'index'
    default_file_extension = '.html'

    # возвращает [str: путь к файлу, str: имя файла]
    def parse_url_in_filepath(self,url):
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
        path = self.folder+path
        # добавим расширение по умолчанию
        file_name = file_name + self.default_file_extension
        return [path, file_name]

    def create_file(self, url):
        pass
        # убираем первый слеш, если есть
        # if url[0]=='/':
        #     url = url[1:]
        # проверяем, есть ли папка с оффлайн версиями страниц
        # if not os.path.exists(self.folder):
        #     os.mkdir(self.folder)

        # os.makedirs(self.folder+url)

    def get_page(self,url):
        pass

    def get_page_status(self, url):
        pass

    def get_page_text(self, url):
        pass

