import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from livelib import *
import logging

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
        cls.db_connection = SQLite3Connection(cls.config.db_config.sqlite_db)
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
        db_con.insert_values('Reader',([{'login':'Ivan'},{'login':'Petr'}]))
        self.object = Reader('Ivan', self.web_connection, db_con)
        res = self.object.has_db_entries()
        print(res)
        remove_file(filename,'Remove test database', 'Can not remove test database')

if __name__=='__main__':
    unittest.main()


