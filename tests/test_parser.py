import unittest

import bs4

from livelib import Parser, WebWithCache
from bs4 import BeautifulSoup as bs
import logging

class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = WebWithCache(folder='data')
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        # структура тестовых данных для reader_prefix, reader_all_books, check_404:
        # логин, префикс_страницы_читателя, все_книги_читателя, страница_404
        self.values = [
            ['serp996', '/reader/serp996', '/reader/serp996/read/listview/smalllist', False],
            ['qwerty5677890', '/reader/qwerty5677890', '/reader/qwerty5677890/read/listview/smalllist', True],

        ]
        # тестовые данные для get_author_id, get_author_name
        self.author_values = [
            ['<a class="brow-book-author" href="/author/22748-vladimir-obruchev" title="Владимир Обручев">Владимир Обручев</a>', 'Владимир Обручев', 22748],
            ['<a class="brow-book-author" href="/author/vladimir-obruchev" title="Владимир Обручев">Владимир Обручев</a>', 'Владимир Обручев', None],
            ['<a class="brow-book-author" href="/author/vladimir-obruchev" title="Владимир Обручев"></a>', None, None],
            ['<a class="brow-book-author111" href="/author/22748-vladimir-obruchev" title="Владимир Обручев">Владимир Обручев</a>', None, None],
        ]

        self.book_values = [
            ['<a class="brow-book-name with-cycle" href="/book/1001130597-zemlya-sannikova-vladimir-obruchev" title="Владимир Обручев - Земля Санникова">Земля Санникова</a>',
             'Земля Санникова', 1001130597],
            ['<a class="brow-book-name with-cycle" href="/book/-zemlya-sannikova-vladimir-obruchev" title="Владимир Обручев - Земля Санникова">Земля Санникова</a>',
             'Земля Санникова', None],
            ['<a class="brow-book-name with-cycle" href="/book/-zemlya-sannikova-vladimir-obruchev" title="Владимир Обручев - Земля Санникова"></a>',
                None, None],
            ['<a class="brow-book-namqqqq with-cycle" href="/book/-zemlya-sannikova-vladimir-obruchev" title="Владимир Обручев - Земля Санникова"></a>',
                None, None],
        ]

        self.rating_values = [
            ['<span class="brow-rating"><span class="rating-book"><span class="rating-value stars-color-orange">4.29</span>'
             '<span title="Рейтинг 4.287 (1906  читателей, рейтинг ожидания 5.000)"><span class="r45-sc-orange"></span></span></span></span>', 4.29],
            [
                '<span class="brow-rating"><span class="rating-book"><span class="rating-value stars-color-orange"></span>'
                '<span title="Рейтинг 4.287 (1906  читателей, рейтинг ожидания 5.000)"><span class="r45-sc-orange"></span></span></span></span>', None],

        ]

        def into_bs(x):
            for i in x:
                i[0] = bs4.BeautifulSoup(i[0], self.connection.bs_parser)
            return x

        # для удобства преобразуем строки в BeautifulSoup
        self.book_values = into_bs(self.book_values)
        self.author_values = into_bs(self.author_values)
        self.rating_values = into_bs(self.rating_values)

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
                text = bs(self.connection.get_page_text(Parser.reader_all_books(i[0])), features=self.connection.bs_parser)
                self.assertEqual(i[3], Parser.check_404(text))

    # вставить данные для отсутствия книжек
    def test_all_books_from_page(self):
        values = ['Feana']
        con = WebWithCache()
        for i in values:
            self.assertGreater(len(Parser.all_books_from_page(con.get_page_bs('http://www.livelib.ru/reader/Feana/read'))),0)

    def test_get_author_name(self):
        for i in self.author_values:
            self.assertEqual(i[1], Parser.get_author_name(i[0]))

    def test_get_author_id(self):
        for i in self.author_values:
            self.assertEqual(i[2], Parser.get_author_id(i[0]))

    def test_get_book_id(self):
        for i in self.book_values:
            self.assertEqual(i[2], Parser.get_book_id(i[0]))

    def test_get_book_name(self):
        for i in self.book_values:
            self.assertEqual(i[1], Parser.get_book_name(i[0]))

    def test_get_common_rating(self):
        for i in self.rating_values:
            self.assertEqual(i[1], Parser.get_common_rating(i[0]))


if __name__=='__main__':
    unittest.main()