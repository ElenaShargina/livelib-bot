import json
import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_correct_filename

import unittest
import bs4

from livelib import Parser, WebWithCache, Config
from bs4 import BeautifulSoup as bs
import logging


class TestParser(unittest.TestCase):
    test_folder = 'data/sample/test_parser'

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_config = Config(get_correct_filename('.env.parser', ''))
        cls.connection = WebWithCache(cls.test_config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")

    def _str_to_bs(self, x: str) -> bs4.BeautifulSoup:
        """
        Служебная функция, переформартирует строку в объект BeautifulSoup в соответствии с настройками экземпляра WebConnection
        """
        return bs4.BeautifulSoup(x, self.connection.bs_parser)

    def process_json_compare_to_json(self, method: str, json_property_name: str, folder: str,
                                     convert_html_to_bs: bool = True) -> None:
        """
        Тестируем методы на небольших кусках html, для удобства вынесенных в отдельный файл file.json вместе с ожидаемыми результатами.
        Структура json файла:
        [{'html':'тестируемый_html_код', '<json_property_name>':'целевое_значения_свойства'}, {}, ...]
        Общая структура папок: <cls.test_folder>/<folder>/file.json
        :param method: название метода Parser, который будем тестировать
        :type method: str
        :param json_property_name: название целевого свойства в json-файле
        :type json_property_name: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        :param convert_html_to_bs: конвертировать ли html в BeautifulSoup
            defaults to True
        :type convert_html_to_bs: bool
        """
        filename = get_correct_filename('file.json', os.path.join(self.test_folder, folder))
        with open(filename, mode='r', encoding=self.test_config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i[json_property_name]}'):
                    input = self._str_to_bs(i['html']) if convert_html_to_bs else i['html']
                    self.assertEqual(i[json_property_name], getattr(Parser, method)(input))

    def process_html_compare_to_json(self, method: str, folder: str, convert_html_to_bs:bool = True) -> None:
        """
        Тестируем на БОЛЬШИХ кусках html, для удобства вынесенных в ОТДЕЛЬНЫЙ файл file.html
        Результат парсинга сравниваем с заранее сохраненными образцами в correct_output.json файлах.
        Общая структура папок: /<folder>/1/file.html, correct_output.json
        :param method: название метода Parser, который будем тестировать
        :type method: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        :param convert_html_to_bs: конвертировать ли html в BeautifulSoup
            defaults to True
        :type convert_html_to_bs: bool
        """
        prefix_folder = os.path.join(get_correct_filename('', self.test_folder), folder)
        # просматриваем, какие папки с тестовыми данными есть в folder
        # в каждой папке должен быть file.html с html кодом и dump, где сохранен правильный результат парсинга
        with os.scandir(prefix_folder) as files:
            subdirs = [file.name for file in files if file.is_dir()]
        # для каждой папки сличаем результат парсинга и правильный сохраненный результат
        for i in subdirs:
            with open(os.path.join(prefix_folder, str(i), 'file.html'), mode='r',
                      encoding=self.connection.encoding) as f1:
                output = getattr(Parser, method)(self._str_to_bs(f1.read()))
                # print(output)
                f1.close()
            # with open(os.path.join(prefix_folder, str(i), 'correct_output.json'), mode='w', encoding=self.connection.encoding) as f3:
            #     json.dump(output,f3, indent=4, ensure_ascii=False)
            #     f3.close()
            with open(os.path.join(prefix_folder, str(i), 'correct_output.json'), mode='r', encoding=self.connection.encoding) as f2:
                correct_output = json.load(f2)
                f2.close()
            with self.subTest(f'Test method {method} with {i} subdir.'):
                # self.assertEqual(True,True)
                self.assertEqual(output, correct_output)

    def test_reader_prefix(self):
        self.process_json_compare_to_json('reader_prefix', 'reader_prefix', 'reader', convert_html_to_bs=False)

    def test_reader_all_books(self):
        self.process_json_compare_to_json('reader_all_books', 'reader_all_books_prefix', 'reader', convert_html_to_bs=False)

    def test_check_404(self):
        """
        В связи с особой обработкой не пользуемся стандартной функцией process_json_compare_to_json
        """
        filename = get_correct_filename('file.json', os.path.join(self.test_folder, 'reader'))
        with open(filename, mode='r', encoding=self.test_config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i["html"]}'):
                    text = bs(self.connection.get_page_text(Parser.reader_all_books(i["html"])),
                              features=self.connection.bs_parser)
                    self.assertEqual(i["404_status"], Parser.check_404(text))


    # @todo вставить данные для отсутствия книжек
    def test_all_books_from_page(self):
        values = ['Feana']
        con = WebWithCache()
        for i in values:
            self.assertGreater(
                len(Parser.all_books_from_page(con.get_page_bs('http://www.livelib.ru/reader/Feana/read'))), 0)

    def test_get_author_name(self):
        self.process_json_compare_to_json('get_author_name', 'author_name', 'author')

    def test_get_author_id(self):
        self.process_json_compare_to_json('get_author_id', 'author_id', 'author')

    def test_get_book_id(self):
        self.process_json_compare_to_json('get_book_id', 'book_id', 'book')

    def test_get_book_name(self):
        self.process_json_compare_to_json('get_book_name', 'book_name', 'book')

    def test_get_common_rating(self):
        self.process_json_compare_to_json('get_common_rating', 'common_rating', 'rating')

    def test_get_reader_rating(self):
        self.process_json_compare_to_json('get_reader_rating', 'reader_rating', 'rating')

    def test_get_picture_url(self):
        self.process_json_compare_to_json('get_picture_url', 'picture_url', 'picture_url')

    def test_all_books_from_page(self):
        self.process_html_compare_to_json('all_books_from_page', 'booklist')

    def test_get_paginator(self):
        self.process_html_compare_to_json('get_paginator', 'paginator')

    def test_get_tags(self):
        self.process_html_compare_to_json('get_tags', 'tags')


if __name__ == '__main__':
    unittest.main()
