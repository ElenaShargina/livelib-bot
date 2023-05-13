import json
import os, sys

# скрипт для правильной отработки тестов в github.actions
import random

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
        cls.web_connection = WebWithCache(cls.config, random_sleep=False)
        db_filename = get_correct_filename(cls.config.db_config.sqlite_db, "")
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

    def test_get_db_id(self):
        with self.subTest(f'Testing correct login'):
            r = Reader('Reader36385266', self.web_connection, self.db_connection)
            self.assertEqual(3, r.get_db_id())
        with self.subTest(f'Testing incorrect login'):
            r = Reader('Petr111111', self.web_connection, self.db_connection)
            self.assertEqual(None, r.get_db_id())

    def test_insert_db_id(self):
        reader_name = 'Reader'+str(random.randint(100_000,100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection)
        new_id = r.insert_into_db()
        check_id = r.get_db_id()
        with self.subTest('Testing adding new Reader '):
            self.assertEqual(new_id, check_id)
        with self.subTest('Testing adding existing Reader '):
            self.assertEqual(new_id, r.insert_into_db())

    def test_fill_update_time(self):
        reader_name = 'Reader'+str(random.randint(100_000,100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection)
        r.register()
        with self.subTest(f'Testing filling update time for Reader {reader_name}'):
            correct_update_time = r.fill_update_time()
            self.assertEqual(correct_update_time, r.get_update_time())

    def test_get_update_time(self):
        reader_name = 'Reader'+str(random.randint(100_000,100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection)
        r.register()
        with self.subTest(f'Testing getting non-existing update time for Reader {reader_name}'):
            self.assertEqual(None, r.get_update_time())
        correct_update_time = str(r.fill_update_time())
        with self.subTest(f'Testing getting update time for Reader {reader_name}'):
            self.assertEqual(correct_update_time, r.get_update_time())

    def test_delete_read_books(self):
        # создаем нового читателя
        reader_name = 'Reader'+str(random.randint(100_000,100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection)
        r.register()

        # сохраняем для него тестовые книги как прочитанные
        filename=get_correct_filename('sample_books.json',os.path.join(self.test_folder, 'delete_read_books'))
        with open(filename, mode='r', encoding='utf-8') as f:
            books = json.load(f)
        saved_books_num = r.save_read_books_in_db(books)
        r.fill_update_time()
        # проверяем, что они добавились с помощью save_books_in_db
        with self.subTest('Checking number of saved books'):
            self.assertEqual(len(books), saved_books_num)

        # проверяем, что они добавились с помощью get_read_books_from_db
        saved_books = r.get_read_books_from_db()
        with self.subTest('Checking number of saved books once more'):
            self.assertEqual(len(books), len(saved_books))

        # удаляем книги читателя
        r.delete_read_books()
        # проверяем, что книги удалились
        with self.subTest('Checking that books are deleted'):
            self.assertEqual(0, len(r.get_read_books_from_db()))

    def test_update_books(self):
        # 1. Создаем нового читателя
        # используем реального читателя с небольшим (60) количеством книг
        reader_name = 'Kasssiopei'
        r = Reader(reader_name, self.web_connection, self.db_connection)
        r.register()
        # 2. Скачиваем книги для него в базу данных
        old_books_num = len(r.get_read_books_from_web())
        old_update_time = r.get_update_time()
        with self.subTest(f'Checking getting books from web for {reader_name}'):
            self.assertGreater(old_books_num, 0)
        # 3. Обновляем его книги
        r.update_books()
        # 4. Проверяем, что книги в базе данных есть.
        new_books_num = len(r.get_read_books_from_db())
        with self.subTest(f'Checking books after update for {reader_name}'):
            self.assertEqual(old_books_num,new_books_num)
        # 5. Проверяем, что время обновления в профиле читателя поменялось
        with self.subTest(f'Checking new update time for {reader_name}'):
            self.assertNotEqual(old_update_time, r.get_update_time())

    def test_get_read_books_from_db(self):
        pass

    def test_get_read_books_from_web(self):
        pass

    def test_save_read_books_in_db(self):
        pass

    def test_register(self):
        pass

    def test_get_read_books_from_page(self):
        pass

    def test_create_export_file(self):
        pass

if __name__=='__main__':
    unittest.main()


