from livelib import Connection
from livelib import SimpleWeb, Offline
import unittest


class Test_SimpleWeb(unittest.TestCase):
    # структура тестовых данных: адрес_сайта, наличие_сайта, код_отзыва
    test_values = [
        ['http://www.example.com', True, 200],
        ['http://example4567.com', False, 0],
        ['http://www.livelib.com', True, 200],
        ['http://www.yandex.com', True, 200],
    ]

    def test_get_page_status(self):
        con = SimpleWeb()
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                self.assertEqual(i[2], con.get_page_status(i[0]))

    def test_get_page(self):
        con = SimpleWeb()
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                if i[1]:
                    # сайт существует
                    self.assertEqual(i[1], bool(con.get_page(i[0])), msg=f'Site should be opened! {i[0]}')
                else:
                    # сайт не существует
                    self.assertRaises(Exception, con.get_page(i[0]), msg=f'Exception is awaited! {i[0]}')

    def test_get_page_text(self):
        con = SimpleWeb()
        for i in self.test_values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                if i[1]:
                    # сайт существует
                    self.assertGreater(len(con.get_page_text(i[0])), 0, msg=f'Text should be found! {i[0]}')
                else:
                    # сайт не существует
                    self.assertEqual(None, con.get_page_text(i[0]), msg=f'No text should be found! {i[0]}')


class Test_Offline(unittest.TestCase):
    test_folder = 'offline_test'

    def test_parse_url_in_filepath(self):
        values = [
            ['http://www.livelib.ru/foo/bar', [self.test_folder + '/foo/', 'bar.html']],
            ['http://www.livelib.ru/foo/bar.html', [self.test_folder + '/foo/', 'bar.html']],
            ['http://www.livelib.ru/foo/2', [self.test_folder + '/foo/', '2.html']],
            ['http://www.livelib.ru/foo/bar/', [self.test_folder + '/foo/bar/', 'index.html']],
            ['http://www.livelib.ru/foo/bar/1.htm', [self.test_folder + '/foo/bar/', '1.html']],
            ['http://www.livelib.ru/1.htm', [self.test_folder+'/', '1.html']],
            ['http://www.livelib.ru/foo/~12', [self.test_folder + '/foo/', '~12.html']],
        ]
        con = Offline()
        con.folder = self.test_folder
        for i in values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                self.assertEqual(i[1], con.parse_url_in_filepath(i[0]))


if __name__ == '__main__':
    unittest.main()
