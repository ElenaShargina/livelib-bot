import os
import shutil
import unittest
import logging
import bs4
import livelib
from livelib import SimpleWeb, WebWithCache, Config
from utils import get_correct_filename


class TestSimpleWeb(unittest.TestCase):
    # структура тестовых данных: адрес_сайта, наличие_сайта, код_отзыва
    test_values = [
        ['http://www.example.com', True, 200],
        ['http://example4567.com', False, 0],
        ['http://www.livelib.com', True, 200],
        ['http://www.yandex.com', True, 200],
    ]
    config_file: str = 'webconnection.env'

    @classmethod
    def setUpClass(cls) -> None:
        cls.config_file = get_correct_filename(filename=cls.config_file, folder='')

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
    test_values = []
    config_file: str = 'webconnection.env'
    test_folder: str

    @classmethod
    def setUpClass(cls) -> None:
        print('first')
        cls.config_file = get_correct_filename(filename=cls.config_file, folder='')
        print('cls.config_file=',cls.config_file)
        test_config = Config(cls.config_file)
        print('test_config=',test_config)
        cls.test_folder = test_config.web_connection.cache_folder
        print('test_folder=',cls.test_folder)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='w',
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.debug('Starting to test')
        if os.path.isdir(cls.test_folder):
            cls._remove_folder(cls.test_folder)
        cls.values_path = [
            ['http://www.livelib.ru/', [cls.test_folder + '/', 'index.html']],
            ['http://www.livelib.ru/foo/bar', [cls.test_folder + '/foo/', 'bar.html']],
            ['http://www.livelib.ru/foo/bar.html', [cls.test_folder + '/foo/', 'bar.html']],
            ['http://www.livelib.ru/foo/2', [cls.test_folder + '/foo/', '2.html']],
            ['http://www.livelib.ru/foo/bar/', [cls.test_folder + '/foo/bar/', 'index.html']],
            ['http://www.livelib.ru/foo/bar/1.htm', [cls.test_folder + '/foo/bar/', '1.html']],
            ['http://www.livelib.ru/1.htm', [cls.test_folder + '/', '1.html']],
            ['http://www.livelib.ru/foo/~12', [cls.test_folder + '/foo/', '~12.html']],
        ]
        cls.values_text = [
            ['1', 'http://www.fontanka.ru', 'http://www.fontanka.ru/', True],
            ['2', 'https://award.fontanka.ru', 'https://award.fontanka.ru/', True],
            ['3', 'http://www.uiiiiioo.ru', 'http://www.uiiiiioo.ru/', False],
            ['4', 'https://www.fontanka.ru', 'https://www.fontanka.ru/theme/ratings/', True]
        ]

    def _remove_folder(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            raise Exception(f"Can not remove folder {path}")


    def tearDown(self) -> None:
        logging.debug('Cleaning dirs and files after testing')
        if os.path.exists(self.test_folder):
            self._remove_folder(self.test_folder)
        pass

    def test_parse_url_in_filepath_and_filename(self):
        config = Config(self.config_file)
        con = WebWithCache(config)
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

    def _test_get_page_text(self):
        # тестовые данные вида [подпапка, сайт, адрес_страницы, ожидается_ли_ответ]
        # подпапки нужны так как в тестовых данных встречаются разные сайты и их нужно разделить
        # в самой программе при штатной работе будет только один сайт
        for i in self.values_text:
            with self.subTest(msg=f'Okey with {i[2]}'):
                config = Config(self.config_file)
                config.web_connection.site = i[1]
                config.web_connection.cache_folder = config.web_connection.cache_folder + '/' + i[0]
                con = WebWithCache(config)
                if i[3]:
                    # сайт существует
                    self.assertGreater(len(con.get_page_text(i[2])), 0, msg=f'Text should be found! {i[2]}')
                else:
                    # сайт не существует
                    with self.assertRaises(Exception):
                        con.get_page_text(i[2])

    def _test__get_page_bs(self):
        # тестовые данные вида [подпапка, сайт, адрес_страницы, ожидается_ли_ответ]
        # подпапки нужны так как в тестовых данных встречаются разные сайты и их нужно разделить
        # в самой программе при штатной работе будет только один сайт
        for i in self.values_text:
            with self.subTest(msg=f'Okey with {i[2]}'):
                config = Config(self.config_file)
                config.web_connection.site = i[1]
                config.web_connection.cache_folder = config.web_connection.cache_folder + '/' + i[0]
                con = WebWithCache(config)
                if i[3]:
                    # сайт существует
                    self.assertGreater(len(con._get_page_bs(i[2])), 0, msg=f'BeautifulSoup should be found! {i[2]}')
                else:
                    # сайт не существует
                    self.assertEqual(con._get_page_bs(i[2]), None, msg=f'BeautifulSoup should not be found! {i[0]}')


if __name__ == '__main__':
    unittest.main()
