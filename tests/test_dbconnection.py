import sqlite3
import unittest
from livelib import SQLite3Connection
import os
from livelib.parser import BookDataFormatter

class TestDBConnection(unittest.TestCase):

    def test_create_table(self):
        with self.subTest('Testing correct case of creating table'):
            filename = self.get_filename_of_db('correct.db')
            con = SQLite3Connection(filename)
            con.create_table('Foo', [{'name':'col1', 'type':'INTEGER'},{'name':'col2','type':'TEXT'}])
            output = con.run_single_sql('PRAGMA table_info(Foo)')
            correct_output = [(0, 'id', 'INTEGER', 1, None, 1), (1, 'col1', 'INTEGER', 0, None, 0), (2, 'col2', 'TEXT', 0, None, 0)]
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

if __name__ == '__main__':
    unittest.main()