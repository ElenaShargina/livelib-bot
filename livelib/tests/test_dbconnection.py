import json
import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_correct_filename, CustomUnitTest

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
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.web_connection = WebWithCache(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML
        print(get_correct_filename(cls.config.db_config.sqlite_db, ""))
        cls.object = SQLite3Connection(get_correct_filename(cls.config.db_config.sqlite_db, ""))

    def test_create_db(self):
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
        # удаляем тестовые таблицы
        self.object.run_single_sql("DROP TABLE IF EXISTS ReadBook")
        self.object.run_single_sql("DROP TABLE IF EXISTS Reader")
        self.object.run_single_sql("DROP TABLE IF EXISTS Book")

    def test_insert_values(self):
        filename = get_correct_filename('insert_values.db', self.test_folder)
        con = SQLite3Connection(filename)
        # con.run_single_sql("CREATE TABLE Foo (col1 INTEGER, col2 TEXT)")
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


    def test_table_exists(self):
        filename = get_correct_filename('db.db', '/data/sample/test_sqlite3/table_exists/')
        con = SQLite3Connection(filename)
        with self.subTest('Testing if table exists'):
            self.assertTrue(con.table_exists('mytable'))
        with self.subTest("Testing if table doesn't exist"):
            self.assertFalse(con.table_exists('notable'))


if __name__ == '__main__':
    unittest.main()
