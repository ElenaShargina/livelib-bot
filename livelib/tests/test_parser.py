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
import pickle


class TestParser(unittest.TestCase):
    test_folder = 'data/sample/test_parser'

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_config = Config(get_correct_filename('.env.parser', ''))
        cls.connection = WebWithCache(cls.test_config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        # структура тестовых данных для reader_prefix, reader_all_books, check_404:
        # логин, префикс_страницы_читателя, все_книги_читателя, страница_404
        cls.values = [
            ['serp996', '/reader/serp996', '/reader/serp996/read/listview/smalllist', False],
            ['qwerty5677890', '/reader/qwerty5677890', '/reader/qwerty5677890/read/listview/smalllist', True],

        ]

    def _str_to_bs(self, x: str) -> bs4.BeautifulSoup:
        """
        Служебная функция, переформартирует строку в объект BeautifulSoup в соответствии с настройками экземпляра WebConnection
        """
        return bs4.BeautifulSoup(x, self.connection.bs_parser)

    def test_reader_prefix(self):
        for i in self.values:
            with self.subTest(msg=f'Test with {i}'):
                self.assertEqual(i[1], Parser.reader_prefix(i[0]))

    def test_reader_all_books(self):
        for i in self.values:
            with self.subTest(msg=f'Test with {i}'):
                self.assertEqual(i[2], Parser.reader_all_books(i[0]))

    def test_check_404(self):
        for i in self.values:
            with self.subTest(msg=f'Test with {i}'):
                text = bs(self.connection.get_page_text(Parser.reader_all_books(i[0])),
                          features=self.connection.bs_parser)
                self.assertEqual(i[3], Parser.check_404(text))

    # вставить данные для отсутствия книжек
    def test_all_books_from_page(self):
        values = ['Feana']
        con = WebWithCache()
        for i in values:
            self.assertGreater(
                len(Parser.all_books_from_page(con.get_page_bs('http://www.livelib.ru/reader/Feana/read'))), 0)

    def compare_results_with_json(self, method: str, json_property_name:str, folder=str) -> None:
        """
        Тестируем на небольших кусках html, для удобства вынесенных в отдельный файл file.json.
        Структура json файла:
        [{'html':'тестируемый_html_код', '<json_property_name>':'целевое_значения_свойства'}, {}, ...]
        Общая структура папок: <cls.test_folder>/<folder>/file.json
        :param method: название метода Parser, который будем тестировать
        :type method: str
        :param json_property_name: название целевого свойства в json-файле
        :type json_property_name: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        """
        filename = get_correct_filename('file.json', os.path.join(self.test_folder,folder))
        with open(filename, mode='r', encoding=self.test_config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i[json_property_name]}'):
                    self.assertEqual(i[json_property_name], getattr(Parser, method)(self._str_to_bs(i['html'])))

    def test_get_author_name(self):
        self.compare_results_with_json('get_author_name','author_name','author')

    def test_get_author_id(self):
        self.compare_results_with_json('get_author_id', 'author_id', 'author')

    def test_get_book_id(self):
        self.compare_results_with_json('get_book_id', 'book_id', 'book')

    def test_get_book_name(self):
        self.compare_results_with_json('get_book_name', 'book_name', 'book')

    def test_get_common_rating(self):
        self.compare_results_with_json('get_common_rating', 'common_rating', 'rating')

    def test_get_reader_rating(self):
        self.compare_results_with_json('get_reader_rating', 'reader_rating', 'rating')

    def test_get_picture_url(self):
        self.compare_results_with_json('get_picture_url', 'picture_url', 'picture_url')

    def compare_results_with_dump(self, method: str, folder: str) -> None:
        """
        Тестируем на больших кусках html, для удобства вынесенных в отдельный файл file.html
        Результат парсинга сравниваем с заранее сохраненными образцами в dump файлах.
        Общая структура папок: /<folder>/1/file.html, dump ; /<folder>/2/file.html, dump.
        :param method: название метода Parser, который будем тестировать
        :type method: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        """
        prefix_folder = os.path.join(get_correct_filename('',self.test_folder), folder)
        # просматриваем, какие папки с тестовыми данными есть в folder
        # в каждой папке должен быть file.html с html кодом и dump, где сохранен правильный результат парсинга
        with os.scandir(prefix_folder) as files:
            subdirs = [file.name for file in files if file.is_dir()]
        # для каждой папки сличаем результат парсинга и правильный сохраненный результат
        for i in subdirs:
            with open(os.path.join(prefix_folder, str(i), 'file.html'), mode='r',
                      encoding=self.connection.encoding) as f1:
                output = getattr(Parser, method)(bs4.BeautifulSoup(f1.read(), self.connection.bs_parser))
                f1.close()
            with open(os.path.join(prefix_folder, str(i), 'dump'), mode='rb') as f2:
                # pickle.dump(output,f2)
                correct_output = pickle.load(f2, encoding=self.connection.encoding)
                f2.close()
            with self.subTest(f'Test method {method} with {i} subdir.'):
                # self.assertEqual(True,True)
                self.assertEqual(output, correct_output)

    def test_all_books_from_page(self):
        self.compare_results_with_dump('all_books_from_page', 'booklist')

    def test_get_paginator(self):
        self.compare_results_with_dump('get_paginator', 'paginator')

    def test_get_tags(self):
        self.compare_results_with_dump('get_tags', 'tags')


if __name__ == '__main__':
    unittest.main()
