import copy
import datetime
import json
import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_correct_filename, CustomUnitTest, remove_file, create_logger_for_tests

import sqlite3
import unittest
from livelib import SQLite3Connection, Config, WebWithCache, BookDataFormatter, ParserFromHTML
import logging


class TestDBConnection(CustomUnitTest):
    # папка с данными для проведения тестов
    # внутри её есть подпапки для конкретных функций
    test_folder: str = 'data/sample/test_sqlite3'
    # файл с конфигом для проведения тестов.
    # тесты имеют собственную папку кеша веб-страниц
    config_file: str = '.env.sqlite3'

    @classmethod
    def setUpClass(cls) -> None:
        create_logger_for_tests(__name__+'.log')
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.web_connection = WebWithCache(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML

    def test_run_single_sql(self):
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('test.db', os.path.join(self.test_folder, 'run_single_sql'))
        self.object = SQLite3Connection(special_config, create_if_not_exist=False)
        self.process_json_compare_to_json('run_single_sql', 'run_single_sql', 'output', 'input',
                                          convert_html_to_bs=False)

    def test_run_single_sql_return_lastrowid(self):
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('test_insert.db',
                                                           os.path.join(self.test_folder, 'run_single_sql'))
        self.object = SQLite3Connection(special_config, create_if_not_exist=True)
        self.object.create_db(BookDataFormatter)
        result = self.object.run_single_sql('INSERT INTO Book (book_name) VALUES ("Тестовая книга")',
                                            return_lastrowid=True)
        self.assertGreater(result, 0)
        remove_file(special_config.db.sqlite_db)

    def test_get_table_schema(self):
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('test.db',
                                                           os.path.join(self.test_folder, 'get_table_schema'))
        self.object = SQLite3Connection(special_config, create_if_not_exist=True)
        self.object.run_single_sql("CREATE TABLE Foo (id INTEGER PRIMARY KEY AUTOINCREMENT, col1 TEXT, col2 INTEGER)")
        result = self.object.get_table_schema('Foo')
        with open(get_correct_filename('file.json', os.path.join(self.test_folder, 'get_table_schema')), mode='r') as f:
            self.assertEqual(result, json.load(f))
        # удаляем тестовую базу данных
        remove_file(special_config.db.sqlite_db, 'Remove test database', 'Can not remove test database')

    def test_create_db(self):
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('test.db', self.test_folder)
        self.object = SQLite3Connection(special_config, create_if_not_exist=True)
        self.object.create_db(BookDataFormatter)
        self.process_json_compare_to_json('get_table_schema', 'create_db', 'output', 'table', convert_html_to_bs=False)
        # код для изменения файла с правильным ответом
        """
        correct_output = []
        for i in ['Book','Reader', 'ReadBook']:
            output = self.object.get_table_schema(i)
            correct_output.append({"table":i, "output":output})
        print(correct_output)
        with open(get_correct_filename('file.json', os.path.join(self.test_folder, 'create_db')), mode='w', encoding='utf-8') as f:
             res = json.dump(correct_output, f, ensure_ascii=True)
        """
        # удаляем тестовую базу данных
        remove_file(special_config.db.sqlite_db, 'Remove test database', 'Can not remove test database')

    def test_insert_values(self):
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('insert_values.db', self.test_folder)
        con = SQLite3Connection(special_config, create_if_not_exist=True)
        con.run_single_sql("CREATE TABLE Foo (col1 INTEGER, col2 TEXT)")
        with self.subTest('Testing correct inserting values'):
            values = [
                {'col1': 1, 'col2': 'smth'},
                {'col1': 12, 'col2': 'smth123'},
                {'col1': 34, 'col2': 2323},
            ]
            correct_output = len(values)
            output = con.insert_values('Foo', values)
            self.assertEqual(output, correct_output)
        with self.subTest('Testing incorrect inserting values'):
            values = [
                [{'col1': 1, }, {'col1': 12, 'col2': 'smth123'}, {'col1': 34, 'col2': 2323}, ],
                [{'col1': 12, 'col2': 'smth123'}, {'col1': 34, }],
                [{'qwerty': 12, 'col2': 'smth123'}, {'col1': 34, }],
                [{'col1': 1, 'col2': 12, 'col3': 'smth123'}, {'col1': 12, 'col2': 'smth123'},
                 {'col1': 34, 'col2': 2323}, ],
            ]
            for i in values:
                with self.assertRaises(Exception):
                    output = con.insert_values('Foo', i)
        # удаляем тестовую базу данных
        remove_file(special_config.db.sqlite_db, 'Remove test database', 'Can not remove test database')

    def test_table_exists(self):
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('db.db', '/data/sample/test_sqlite3/table_exists/')
        con = SQLite3Connection(special_config)
        with self.subTest('Testing if table exists'):
            self.assertTrue(con.table_exists('mytable'))
        with self.subTest("Testing if table doesn't exist"):
            self.assertFalse(con.table_exists('notable'))


if __name__ == '__main__':
    unittest.main()
