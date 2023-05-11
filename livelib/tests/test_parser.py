import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import json
import bs4
from bs4 import BeautifulSoup as bs
import logging

from utils import get_correct_filename
from livelib import Parser, WebWithCache, Config


class TestParser(unittest.TestCase):
    # папка с данными для проведения тестов
    # внутри её есть подпапки для конкретных функций
    test_folder: str = 'data/sample/test_parser'
    # файл с конфигом для проведения тестов.
    # тесты имеют собственную папку кеша веб-страниц
    config_file: str = '.env.parser'

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.connection = WebWithCache(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")

    def _str_to_bs(self, x: str) -> bs4.BeautifulSoup:
        """
        Служебная функция, переформартирует строку в объект BeautifulSoup
        в соответствии с настройками имеющегося экземпляра WebConnection
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
        with open(filename, mode='r', encoding=self.config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i[json_property_name]}'):
                    input = self._str_to_bs(i['html']) if convert_html_to_bs else i['html']
                    self.assertEqual(i[json_property_name], getattr(Parser, method)(input))

    def process_html_compare_to_json(self, method: str, folder: str, convert_html_to_bs: bool = True) -> None:
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
        # просматриваем, какие папки с тестовыми данными есть в <folder>
        # в каждой папке должен быть file.html с html кодом и dump.json, где сохранен правильный ответ парсинга
        with os.scandir(prefix_folder) as files:
            subdirs = [file.name for file in files if file.is_dir()]
        # для каждой папки сличаем результат парсинга и правильный сохраненный ответ
        for i in subdirs:
            with open(os.path.join(prefix_folder, str(i), 'file.html'), mode='r',
                      encoding=self.connection.encoding) as f1:
                output = getattr(Parser, method)(self._str_to_bs(f1.read()))
                print(output)
                f1.close()
            # код для обновления файлов с правильными ответами
            with open(os.path.join(prefix_folder, str(i), 'correct_output.json'), mode='w', encoding=self.connection.encoding) as f3:
                json.dump(output,f3, indent=4, ensure_ascii=False)
                f3.close()
            with open(os.path.join(prefix_folder, str(i), 'correct_output.json'), mode='r',
                      encoding=self.connection.encoding) as f2:
                correct_output = json.load(f2)
                f2.close()
            with self.subTest(f'Test method {method} with {i} subdir.'):
                # self.assertEqual(True,True)
                self.assertEqual(output, correct_output)

    def test_reader_prefix(self):
        self.process_json_compare_to_json('reader_prefix', 'reader_prefix', 'reader', convert_html_to_bs=False)

    def test_reader_all_books_page(self):
        self.process_json_compare_to_json('reader_read_books_page', 'reader_read_books_page', 'reader',
                                          convert_html_to_bs=False)
    def test_check_404(self):
        """
        В связи с особой обработкой не пользуемся стандартной функцией process_json_compare_to_json
        """
        filename = get_correct_filename('file.json', os.path.join(self.test_folder, 'reader'))
        with open(filename, mode='r', encoding=self.config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i["html"]}'):
                    text = bs(self.connection.get_page_text(Parser.reader_read_books_page(i["html"])),
                              features=self.connection.bs_parser)
                    self.assertEqual(i["404_status"], Parser.check_404(text))

    def test_get_author_name(self):
        self.process_json_compare_to_json('get_author_name', 'author_name', 'author')

    def test_get_author_id(self):
        self.process_json_compare_to_json('get_author_id', 'author_id', 'author')

    def test_get_book_id(self):
        self.process_json_compare_to_json('get_book_id', 'book_id', 'book_name_id')

    def test_get_book_name(self):
        self.process_json_compare_to_json('get_book_name', 'book_name', 'book_name_id')

    def test_get_work_id(self):
        self.process_json_compare_to_json('get_work_id', 'work_id', 'work_id')

    def test_get_common_rating(self):
        self.process_json_compare_to_json('get_common_rating', 'common_rating', 'rating')

    def test_get_reader_rating(self):
        self.process_json_compare_to_json('get_reader_rating', 'reader_rating', 'rating')

    def test_get_picture_url(self):
        self.process_json_compare_to_json('get_picture_url', 'picture_url', 'picture_url')

    def test_get_book(self):
        self.process_html_compare_to_json('book', 'book')

    def test_all_books_from_page(self):
        self.process_html_compare_to_json('all_books_from_page', 'booklist')

    def test_get_paginator(self):
        self.process_html_compare_to_json('get_paginator', 'paginator')

    def test_get_tags(self):
        self.process_html_compare_to_json('get_tags', 'tags')

    def test_get_review_text(self):
        self.process_html_compare_to_json('get_review_text', 'review_text')

    def test_get_review_id(self):
        self.process_html_compare_to_json('get_review_id', 'review_id')


if __name__ == '__main__':
    unittest.main()
