import unittest
from livelib import *


class TestReader(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = WebWithCache(folder='data')
        # структура тестовых данных:
        # логин, префикс_страницы_читателя, все_книги_читателя, страница_404
        self.values = [
            ['serp996', False],
            ['qwerty5677890', True],

        ]
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")

    def test_get_main_page(self):
        for i in self.values:
            with self.subTest(msg=f'Okey with {i}'):
                r = Reader(i[0], connection=self.connection, bsparser=BSParser)
                # Если читатель не найден, статус 404
                if i[1]:
                    self.assertRaises(Exception, r.get_main_page())
                #   Если читатель найден
                else:
                    self.assertGreater(len(r.get_main_page()), 0)
