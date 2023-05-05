import sqlite3
import unittest
from livelib import SQLite3Connection
import os
from livelib.parser import BookDataFormatter
import logging

class TestDBConnection(unittest.TestCase):

    temp_dbs = []

    def setUp(self) -> None:
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='w',
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.debug('Starting to test TestDBConnection')

    # def tearDown(self) -> None:
    #     logging.debug('Cleaning dbs after testing')
    #     print('CLEARING')
    #     print(self.temp_dbs)
    #     for i in self.temp_dbs:
    #         if os.path.exists(i):
    #             os.remove(i)
    #     pass

    def test_create_table(self):
        with self.subTest('Testing correct case of creating table'):
            filename = self.get_filename_of_db('correct.db')
            con = SQLite3Connection(filename)
            self.temp_dbs.append(filename)
            con.create_table('Foo', [{'name':'col1', 'type':'INTEGER'},{'name':'col2','type':'TEXT'}])
            output = con.run_single_sql('PRAGMA table_info(Foo)')
            correct_output = [(0, 'id', 'INTEGER', 0, None, 1), (1, 'col1', 'INTEGER', 0, None, 0), (2, 'col2', 'TEXT', 0, None, 0)]
            self.assertEqual(output,correct_output)
        #     не удаляем файл с бд, он пригодится в следующем кейсе

        with self.subTest('Testing incorrect case of creating table: The table already exists. '):
            filename = self.get_filename_of_db('correct.db')
            con = SQLite3Connection(filename)
            with self.assertRaises(sqlite3.Error):
                con.create_table('Foo', [{'name': 'col1', 'type': 'INTEGER'}, {'name': 'col2', 'type': 'TEXT'}])
            # удаляем файл с бд
            os.remove(filename)

    def get_filename_of_db(self, filename='test.db', folder='/db/',):
        """
        служебная функция для получения корректного пути до тестовых баз данных,
        нужна для правильной отработки тестов в Github Actions
        """
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        prefix_folder = os.path.join(parent_dir, *folder.split('/'))
        return os.path.join(prefix_folder, filename)

    def test_insert_values(self):
        filename = self.get_filename_of_db('insert_values.db')
        con = SQLite3Connection(filename)
        self.temp_dbs.append(filename)
        con.create_table('Foo', [{'name': 'col1', 'type': 'INTEGER'}, {'name': 'col2', 'type': 'TEXT'}])
        with self.subTest('Testing correct inserting values'):
            values = [
                {'col1': 1, 'col2': 'smth'},
                {'col1': 12, 'col2': 'smth123'},
                {'col1': 34, 'col2': 2323},
            ]
            correct_output = len(values)
            output = con.insert_values('Foo',values)
            self.assertEqual(output,correct_output)
        with self.subTest('Testing incorrect inserting values'):
            values = [
                [{'col1': 1, },{'col1': 12, 'col2': 'smth123'},{'col1': 34, 'col2': 2323},],
                [{'col1': 12, 'col2': 'smth123'}, {'col1': 34, } ],
                [{'qwerty': 12, 'col2': 'smth123'}, {'col1': 34, }],
                [{'col1': 1, 'col2': 12, 'col3': 'smth123'}, {'col1': 12, 'col2': 'smth123'}, {'col1': 34, 'col2': 2323}, ],
            ]
            for i in values:
                with self.assertRaises(Exception):
                    output = con.insert_values('Foo', i)
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()