import unittest
from livelib import BSParser, WebWithCache
from bs4 import BeautifulSoup as bs
import logging

class Test_BSParser(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = WebWithCache(folder='data')
        # структура тестовых данных:
        # логин, префикс_страницы_читателя, все_книги_читателя, страница_404
        self.values = [
            ['serp996', '/reader/serp996', '/reader/serp996/read/listview/smalllist', False],
            ['qwerty5677890', '/reader/qwerty5677890', '/reader/qwerty5677890/read/listview/smalllist', True],

        ]
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a', format="%(asctime)s %(levelname)s %(message)s")

    def test_reader_prefix(self):
        for i in self.values:
            with self.subTest(msg=f'Okey with {i}'):
                self.assertEqual(i[1], BSParser.reader_prefix(i[0]))

    def test_reader_all_books(self):
        for i in self.values:
            with self.subTest(msg=f'Okey with {i}'):
                self.assertEqual(i[2], BSParser.reader_all_books(i[0]))

    def test_check_404(self):
        for i in self.values:
            with self.subTest(msg=f'Okey with {i}'):
                text = bs(self.connection.get_page_text(BSParser.reader_all_books(i[0])), features=self.connection.bs_parser)
                self.assertEqual(i[3], BSParser.check_404(text))