import requests
import os
import re
import logging

class Connection:
    def __init__(self, site='http://www.livelib.ru', bs_parser='lxml', encoding='utf-8'):
        self.site = site
        self.bs_parser = bs_parser
        self.encoding = encoding

    def _get_page(self,url):
        pass

    def get_page_status(self, url):
        pass

    def get_page_text(self, url):
        pass


class SimpleWeb(Connection):
    def _get_page(self, url):
        # если начало url - не ссылка на сайт, то добавляем
        if url[0]=='/':
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
        except Exception as exc:
            logging.debug(f'Can not open this page! {exc}')
            return False

    def get_page_status(self, url):
        try:
            return self._get_page(url).status_code
        except Exception:
            return 0

    def get_page_text(self, url):
        try:
            return self._get_page(url).text
        except Exception:
            return None

class Offline(Connection):
    folder = 'offline'
    default_file_name = 'index'
    default_file_extension = '.html'

    def __init__(self, site='http://www.livelib.ru', bs_parser='lxml', encoding='utf-8', folder = 'offline'):
        self.site = site
        self.bs_parser = bs_parser
        self.encoding = encoding
        self.folder = folder

    # возвращает [str: путь к файлу, str: имя файла]
    def _parse_url_in_filepath_and_filename(self,url):
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

    def _create_file(self, url, text=''):
        path, file_name = self._parse_url_in_filepath_and_filename(url)
        # проверяем, существует ли файл
        if not os.path.isfile(path + file_name):
            # создадим весь путь из папок до нужного файла
            dirs = path.split('/')
            path_dir = ''
            for i in range(len(dirs)):
                path_dir = '/'.join(dirs[:i+1])
                logging.debug(f'Dir {path_dir} is found? {os.path.isdir(path_dir)}')
                if not os.path.isdir(path_dir):
                    logging.debug(f'Create dir {path_dir}')
                    os.mkdir(path_dir)
            # создаем файл
            try:
                my_file = open(path+file_name, mode='x', encoding=self.encoding)
                my_file.write(text)
                logging.debug(f'Create file {my_file} ')
                my_file.close()
            except Exception as exc:
                logging.exception(f'Can not open file for offline connection at {path}{file_name} . {exc}')
                return False
        # открываем вновь созданный или имеющийся файл
        try:
            logging.debug(f'already have {path+file_name}')
            f = open(path + file_name, mode='r', encoding=self.encoding)
            return f
        except Exception as exc:
            logging.exception(f'Can not open file for offline connection at {path}{file_name} . {exc}')
            return False


    def _get_page(self, url):
        path, file_name = self._parse_url_in_filepath_and_filename(url)
        # если страница уже есть в дампе, то возвращаем текст из файла
        if os.path.isfile(path+file_name):
            logging.debug(f'Page {url} is in dump.')
            try:
                f = open(path+file_name, mode='r', encoding=self.encoding)
                result = f.read()
                f.close()
                return result
            except Exception as exc:
                logging.exception(f'Can not load file {path}{file_name} , {exc}')
        # если нет, вызываем ее через simpleweb и сохраняем в дампе
        else:
            web = SimpleWeb(site=self.site,bs_parser=self.bs_parser, encoding=self.encoding)
            web_text = web.get_page_text(url)
            if web_text:
                f = self._create_file(url, web_text)
                result = f.read()
                f.close()
                return result
            else:
                return None


    def get_page_status(self, url):
        result = self._get_page(url)
        if len(result)>0:
            return 200
        else:
            return 0
        return result


    def get_page_text(self, url):
        result = self._get_page(url)
        return result

