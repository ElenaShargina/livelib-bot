import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import json
import bs4
from bs4 import BeautifulSoup as bs
import logging

from utils import get_correct_filename, CustomUnitTest
from livelib import Parser, ParserFromHTML, WebWithCache, Config

class TestParser(CustomUnitTest):
    pass

class TestParserfromHTML(TestParser):
    # папка с данными для проведения тестов
    # внутри её есть подпапки для конкретных функций
    test_folder: str = 'data/sample/test_parser'
    # файл с конфигом для проведения тестов.
    # тесты имеют собственную папку кеша веб-страниц
    config_file: str = '.env.parser'

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.web_connection = WebWithCache(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML
        cls.object = ParserFromHTML

    def test_check_404(self):
        """
        В связи с особой обработкой не пользуемся стандартной функцией process_json_compare_to_json
        """
        filename = get_correct_filename('file.json', os.path.join(self.test_folder, 'reader'))
        with open(filename, mode='r', encoding=self.config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i["html"]}'):
                    text = bs(self.web_connection.get_page_text(self.parser.reader_read_books_page(i["html"])),
                              features=self.web_connection.bs_parser)
                    self.assertEqual(i["404_status"], self.parser.check_404(text))

    def test_reader_prefix(self):
        self.process_json_compare_to_json('reader_prefix', 'reader', 'reader_prefix', convert_html_to_bs=False)

    def test_reader_all_books_page(self):
        self.process_json_compare_to_json('reader_read_books_page', 'reader', 'reader_read_books_page',
                                          convert_html_to_bs=False)
    def test_get_author_name(self):
        self.process_json_compare_to_json('get_author_name', 'author', 'author_name')

    def test_get_author_id(self):
        self.process_json_compare_to_json('get_author_id',  'author', 'author_id')

    def test_get_book_id(self):
        self.process_json_compare_to_json('get_book_id',  'book_name_id', 'book_id')

    def test_get_book_name(self):
        self.process_json_compare_to_json('get_book_name',  'book_name_id', 'book_name')

    def test_get_work_id(self):
        self.process_json_compare_to_json('get_work_id', 'work_id', 'work_id')

    def test_get_common_rating(self):
        self.process_json_compare_to_json('get_common_rating', 'rating', 'common_rating')

    def test_get_reader_rating(self):
        self.process_json_compare_to_json('get_reader_rating', 'rating', 'reader_rating' )

    def test_get_picture_url(self):
        self.process_json_compare_to_json('get_picture_url',  'picture_url', 'picture_url')

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

class TestParserForDB(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
