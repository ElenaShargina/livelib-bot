import os
import shutil
import unittest
import logging
import bs4
import livelib
from livelib import SimpleWeb, WebWithCache, Config
import utils


class TestSimpleWeb(unittest.TestCase):
    # структура тестовых данных: адрес_сайта, наличие_сайта, код_отзыва
    test_values = [
        ['http://www.example.com', True, 200],
        ['http://example4567.com', False, 0],
        ['http://www.livelib.com', True, 200],
        ['http://www.yandex.com', True, 200],
    ]
    config_file: str = '.env'

    @classmethod
    def setUp(cls) -> None:
        cls.config_file = utils.get_filename_of_env(filename='.env', folder='')
        print(cls.config_file)

    def test_get_page_status(self):
        con = SimpleWeb(Config(self.config_file))
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                self.assertEqual(i[2], con.get_page_status(i[0]))

    def test_get_page(self):
        con = SimpleWeb(Config(self.config_file))
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                if i[1]:
                    # сайт существует
                    self.assertEqual(i[1], bool(con._get_page(i[0])), msg=f'Site should be opened! {i[0]}')
                else:
                    # сайт не существует
                    with self.assertRaises(Exception):
                        con._get_page(i[0])

    def test_get_page_text(self):
        con = SimpleWeb(Config(self.config_file))
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                if i[1]:
                    # сайт существует
                    self.assertGreater(len(con.get_page_text(i[0])), 0, msg=f'Text should be found! {i[0]}')
                else:
                    # сайт не существует
                    with self.assertRaises(Exception):
                        con.get_page_text(i[0])

    def test__get_page_bs(self):
        con = SimpleWeb(Config(self.config_file))
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                if i[1]:
                    # сайт существует
                    self.assertGreater(len(con._get_page_bs(i[0])), 0, msg=f'BeautifulSoup should be found! {i[0]}')
                else:
                    # сайт не существует
                    self.assertEqual(None, con._get_page_bs(i[0]))

    def test_get_page_bs(self):
        test_values = [
            ['http://www.example.com', True],
            ['http://example4567.com', False],
            ['http://www.livelib.com', True],
            ['http://www.livelib.com/jsndjsdnljdncldn/', True],
            ['http://www.livelib.ru/reader/alkasnmklas', False],
            ['http://www.livelib.com/reader/feana', True],
            ['http://www.yandex.com', True],
        ]
        con = SimpleWeb(Config(self.config_file))
        for i in test_values:
            with self.subTest(msg=f'Test with {i[0]}'):
                if i[1]:
                    # сайт существует
                    self.assertEqual(type(con.get_page_bs(i[0])), bs4.BeautifulSoup,
                                     msg=f'BeautifulSoup should be found! {i[0]}')
                else:
                    # сайт не существует либо страница на livelib выдает 404
                    self.assertEqual(False, con.get_page_bs(i[0]))


class TestWebWithCache(unittest.TestCase):
    test_folder = 'web_with_cache_test'
    test_values = []
    config_file: str = '.env'

    def _remove_folder(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            raise Exception(f"Can not remove folder {path}")

    def setUp(self) -> None:
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='w',
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.debug('Starting to test')
        if os.path.isdir(self.test_folder):
            self._remove_folder(self.test_folder)
        self.values_path = [
            ['http://www.livelib.ru/', [self.test_folder + '/', 'index.html']],
            ['http://www.livelib.ru/foo/bar', [self.test_folder + '/foo/', 'bar.html']],
            ['http://www.livelib.ru/foo/bar.html', [self.test_folder + '/foo/', 'bar.html']],
            ['http://www.livelib.ru/foo/2', [self.test_folder + '/foo/', '2.html']],
            ['http://www.livelib.ru/foo/bar/', [self.test_folder + '/foo/bar/', 'index.html']],
            ['http://www.livelib.ru/foo/bar/1.htm', [self.test_folder + '/foo/bar/', '1.html']],
            ['http://www.livelib.ru/1.htm', [self.test_folder + '/', '1.html']],
            ['http://www.livelib.ru/foo/~12', [self.test_folder + '/foo/', '~12.html']],
        ]
        self.values_text = [
            ['1', 'http://www.fontanka.ru', 'http://www.fontanka.ru/', True],
            ['2', 'https://award.fontanka.ru', 'https://award.fontanka.ru/', True],
            ['3', 'http://www.uiiiiioo.ru', 'http://www.uiiiiioo.ru/', False],
            ['4', 'https://www.fontanka.ru', 'https://www.fontanka.ru/theme/ratings/', True]
        ]

    def tearDown(self) -> None:
        logging.debug('Cleaning dirs and files after testing')
        if os.path.exists(self.test_folder):
            self._remove_folder(self.test_folder)
        pass

    def test_parse_url_in_filepath_and_filename(self):
        con = WebWithCache(Config(self.config_file))
        for i in self.values_path:
            with self.subTest(msg=f'Okey with {i[0]}'):
                self.assertEqual(i[1], con._parse_url_in_filepath_and_filename(i[0]))

    def test_create_file(self):
        con = WebWithCache(Config(self.config_file))
        for i in self.values_path:
            with self.subTest(msg=f'Okey with {i[0]}'):
                new_file = con._create_file(i[0])
                self.assertEqual(True, os.path.isfile(i[1][0] + i[1][1]))
                new_file.close()

    def test_get_page_text(self):
        # тестовые данные вида [подпапка, сайт, адрес_страницы, ожидается_ли_ответ]
        # подпапки нужны так как в тестовых данных встречаются разные сайты и их нужно разделить
        # в самой программе при штатной работе будет только один сайт
        for i in self.values_text:
            with self.subTest(msg=f'Okey with {i[2]}'):
                config = Config(self.config_file)
                config.web_connection.site = i[1]
                config.web_connection.cache_folder = self.test_folder + '/' + i[0]
                con = WebWithCache(config)
                if i[3]:
                    # сайт существует
                    self.assertGreater(len(con.get_page_text(i[2])), 0, msg=f'Text should be found! {i[2]}')
                else:
                    # сайт не существует
                    with self.assertRaises(Exception):
                        con.get_page_text(i[2])

    def test__get_page_bs(self):
        # тестовые данные вида [подпапка, сайт, адрес_страницы, ожидается_ли_ответ]
        # подпапки нужны так как в тестовых данных встречаются разные сайты и их нужно разделить
        # в самой программе при штатной работе будет только один сайт
        for i in self.values_text:
            with self.subTest(msg=f'Okey with {i[2]}'):
                config = Config(self.config_file)
                config.web_connection.site = i[1]
                config.web_connection.cache_folder = self.test_folder + '/' + i[0]
                con = WebWithCache(config)
                if i[3]:
                    # сайт существует
                    self.assertGreater(len(con._get_page_bs(i[2])), 0, msg=f'BeautifulSoup should be found! {i[2]}')
                else:
                    # сайт не существует
                    self.assertEqual(con._get_page_bs(i[2]), None, msg=f'BeautifulSoup should not be found! {i[0]}')


if __name__ == '__main__':
    unittest.main()
