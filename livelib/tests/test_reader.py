import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from livelib import *
import logging
import datetime

from utils import get_correct_filename, CustomUnitTest, remove_file


class TestReader(CustomUnitTest):
    # папка с данными для проведения тестов
    # внутри её есть подпапки для конкретных функций
    test_folder: str = 'data/sample/test_reader'
    # файл с конфигом для проведения тестов.
    # тесты имеют собственную папку кеша веб-страниц
    config_file: str = '.env.reader'

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.web_connection = WebWithCache(cls.config)
        db_filename = get_correct_filename(cls.config.db_config.sqlite_db)
        cls.db_connection = SQLite3Connection(db_filename)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML

    def test_exists(self):
        self.object = Reader('Somebody', self.web_connection,self.db_connection)
        self.process_json_compare_to_json('exists','exists','exists','input', convert_html_to_bs=False)

    def test_has_db_entries(self):
        # подготавливаем базу данных
        filename = get_correct_filename('test_has_db_entries.db', self.test_folder)
        db_con = SQLite3Connection(filename,create_if_not_exist=True)
        db_con.create_db(BookDataFormatter)
        now = str(datetime.datetime.now())
        test_values = [
            {'login': 'Ivan', 'update_time': now, 'exists' : True},
            {'login': 'Petr', 'update_time': None, 'exists' : True},
            {'login': 'PetrTY', 'update_time': None, 'exists' : False},
            {'login': 'PetrTY', 'update_time': now, 'exists': False},
        ]
        db_con.insert_values('Reader',([{'login':i['login'],'update_time':i['update_time']} for i in test_values if i['exists']]))
        for i in test_values:
            self.object = Reader(i['login'], self.web_connection, db_con)
            if i['exists']:
                with self.subTest('Testing users with existing db_entries'):
                    self.assertEqual(i['update_time'],self.object.has_db_entries())
            else:
                with self.subTest('Testing users with non-existing db_entries'):
                    self.assertEqual(None,self.object.has_db_entries())
        # удаляем тестовую базу данных
        remove_file(filename,'Remove test database', 'Can not remove test database')

if __name__=='__main__':
    unittest.main()


