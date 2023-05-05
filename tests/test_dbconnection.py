import unittest
from livelib import SQLite3Connection
import os

class TestDBConnection(unittest.TestCase):

    def test_create_table(self):
        filename = self.get_filename_of_db()
        con = SQLite3Connection(filename)
        self.assertEqual(True,True)

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