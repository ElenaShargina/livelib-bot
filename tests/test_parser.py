import unittest
import os
import bs4

from livelib import Parser, WebWithCache
from bs4 import BeautifulSoup as bs
import logging
import pickle

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
            [
                """
                <div class="brow-ratings">Моя оценка:<span class="brow-rating marg-right"><span class="rating-book">
                <span class="rating-value stars-color-gray">3</span><span class="rating" style="" title="Нейтральная оценка">
                <span class="r30-sc-gray" title="рейтинг 3 из 5"></span></span></span></span>Общая:<span class="brow-rating">
                <span class="rating-book"><span class="rating-value stars-color-orange">3.84</span>
                <span title="Рейтинг 3.836 (281  читатель, рейтинг ожидания 0.000)"><span class="r40-sc-orange"></span></span></span></span></div>
                """, 3.84, 3
            ],
        ]
        self.picture_url_values = [
            ["""
            <div class="cover-wrapper"><a href="/book/1000945667-svodya-schety-vudi-allen" title="Вуди Аллен - Сводя счеты">
            <img alt="Вуди Аллен - Сводя счеты" title="Вуди Аллен - Сводя счеты" width="70" style="min-width:70px; background-color: #ffffff;" 
            class="cover-rounded" src="https://s1.livelib.ru/boocover/1000945667/70/fbda/Vudi_Allen__Svodya_schety.jpg" 
            onerror="this.onerror=null;pagespeed.lazyLoadImages.loadIfVisibleAndMaybeBeacon(this);"></a></div>
             """,
             'https://s1.livelib.ru/boocover/1000945667/70/fbda/Vudi_Allen__Svodya_schety.jpg'],
            ["""
            <div class="cover-wrapper"> <a href="/book/1000188660-broshennye-mashiny-dzheff-nun" title="Джефф Нун - Брошенные машины">
             <img alt="Джефф Нун - Брошенные машины" class="cover-rounded" 
        data-pagespeed-lazy-src="https://s1.livelib.ru/boocover/1000188660/70/919a/Dzheff_Nun__Broshennye_mashiny.jpg" 
        onerror="this.onerror=null;pagespeed.lazyLoadImages.loadIfVisibleAndMaybeBeacon(this);" 
        onload="pagespeed.lazyLoadImages.loadIfVisibleAndMaybeBeacon(this);" src="/pagespeed_static/1.JiBnMqyl6S.gif" 
        style="min-width:70px; background-color: #ffffff;" title="Джефф Нун - Брошенные машины" width="70"/></a></div>
        """,
             'https://s1.livelib.ru/boocover/1000188660/70/919a/Dzheff_Nun__Broshennye_mashiny.jpg'
            ]
        ]

        def into_bs(x):
            for i in x:
                i[0] = bs4.BeautifulSoup(i[0], self.connection.bs_parser)
            return x

        # для удобства преобразуем строки в BeautifulSoup
        self.book_values = into_bs(self.book_values)
        self.author_values = into_bs(self.author_values)
        self.rating_values = into_bs(self.rating_values)
        self.picture_url_values = into_bs(self.picture_url_values)

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

    def test_get_reader_rating(self):
        for i in self.rating_values:
            self.assertEqual(i[2], Parser.get_reader_rating(i[0]))

    def test_get_picture_url(self):
        for i in self.picture_url_values:
            self.assertEqual(i[1], Parser.get_picture_url(i[0]))

    def compare_results_with_dump(self, method: str, folder: str) -> None:
        """
        Тестируем на больших кусках html, для удобства вынесенных в отдельный файл file.html
        Результат парсинга сравниваем с заранее сохраненными образцами в dump файлах.
        Общая структура папок: /folder/1/file.html, dump ; /folder/2/file.html, dump.
        :param method: название метода Parser, который будем тестировать
        :type method: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        """
        # тестируем на больших кусках html, для удобства вынесенных в отдельный файл file.html
        # результат парсинга сравниваем с заранее сохраненными образцами в dump файлах
        # общая структура папок: /folder/1/file.html, dump ; /folder/2/file.html, dump
        # определяем текущую директорию, строим корректный путь до папок с тестовыми данными
        # нужно для автоматического тестирования на github
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        prefix_folder = os.path.join(parent_dir, *folder.split('/'))
        # просматриваем, какие папки с тестовыми данными есть в folder
        # в каждой папке должен быть file.html с html кодом и dump, где сохранен правильный результат парсинга
        with os.scandir(prefix_folder) as files:
            subdirs = [file.name for file in files if file.is_dir()]
        # для каждой папки сличаем результат парсинга и правильный сохраненный результат
        for i in subdirs:
            with open(os.path.join(prefix_folder, str(i), 'file.html'), mode='r',
                      encoding=self.connection.encoding) as f1:
                output = getattr(Parser,method)(bs4.BeautifulSoup(f1.read(), self.connection.bs_parser))
                f1.close()
            with open(os.path.join(prefix_folder, str(i), 'dump'), mode='rb') as f2:
                correct_output = pickle.load(f2, encoding=self.connection.encoding)
                f2.close()
            with self.subTest(f'Test method {method} with {i} subdir.'):
                self.assertEqual(output, correct_output)

    def test_all_books_from_page(self):
        self.compare_results_with_dump('all_books_from_page', '/data/sample/booklist/')

    def test_get_paginator(self):
        self.compare_results_with_dump('get_paginator', '/data/sample/paginator/')

    def test_get_tags(self):
        self.compare_results_with_dump('get_tags', '/data/sample/tags/')

if __name__=='__main__':
    unittest.main()
