import copy
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
        cls.config.web_connection.cache_folder = get_correct_filename('',cls.config.web_connection.cache_folder)
        # print('NEW CACHE '+cls.config.web_connection.cache_folder)
        cls.web_connection = WebWithCache(cls.config, random_sleep=False)
        cls.config.db.sqlite_db = get_correct_filename(cls.config.db.sqlite_db, "")
        cls.db_connection = SQLite3Connection(cls.config)
        cls.export = XLSXExport(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML

    def test_exists(self):
        values = [
            {"input": "qwertyuioop", "exists": False},
            {"input": "zverek_alyona", "exists": True},
            {"input": "&knla", "exists": False},
            {"input": "", "exists": False},
            {"input": "\\reader\\", "exists": False}
        ]
        special_web_connection = SimpleWeb(self.config, random_sleep=True)
        for i in values:
            with self.subTest(f'Checking if reader {i["input"]} exists ({i["exists"]})'):
                r = Reader(None, special_web_connection, self.db_connection, self.export)
                self.assertEqual(r.exists(i['input']), i['exists'])
                # r = Reader(None, SimpleWeb(self.config), self.db_connection,self.export)
                # self.assertEqual(r.exists(i['input']), i['exists'])

    def test_has_db_entries(self):
        # подготавливаем базу данных
        special_config = copy.deepcopy(self.config)
        special_config.db.sqlite_db = get_correct_filename('test_has_db_entries.db', self.test_folder)
        db_con = SQLite3Connection(special_config, create_if_not_exist=True)
        db_con.create_db(BookDataFormatter)
        now = str(datetime.datetime.now())
        test_values = [
            {'login': 'Ivan', 'update_time': now, 'exists': True},
            {'login': 'Petr', 'update_time': None, 'exists': True},
            {'login': 'PetrTY', 'update_time': None, 'exists': False},
            {'login': 'PetrTY', 'update_time': now, 'exists': False},
        ]
        db_con.insert_values('Reader', (
        [{'login': i['login'], 'update_time': i['update_time']} for i in test_values if i['exists']]))
        for i in test_values:
            self.object = Reader(i['login'], self.web_connection, db_con, self.export)
            if i['exists']:
                with self.subTest('Testing users with existing db_entries'):
                    self.assertEqual(i['update_time'], self.object.has_db_entries())
            else:
                with self.subTest('Testing users with non-existing db_entries'):
                    self.assertEqual(None, self.object.has_db_entries())
        # удаляем тестовую базу данных
        remove_file(special_config.db.sqlite_db, 'Remove test database', 'Can not remove test database')

    def test_get_db_id(self):
        with self.subTest(f'Testing correct login'):
            r = Reader('Reader36385266', self.web_connection, self.db_connection, self.export)
            self.assertEqual(3, r._get_db_id())
        with self.subTest(f'Testing incorrect login'):
            r = Reader('Petr111111', self.web_connection, self.db_connection, self.export)
            self.assertEqual(None, r._get_db_id())

    def test_insert_db_id(self):
        reader_name = 'Reader' + str(random.randint(100_000, 100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        new_id = r._insert_into_db()
        check_id = r._get_db_id()
        with self.subTest('Testing adding new Reader '):
            self.assertEqual(new_id, check_id)
        with self.subTest('Testing adding existing Reader '):
            self.assertEqual(new_id, r._insert_into_db())

    def test_fill_update_time(self):
        reader_name = 'Reader' + str(random.randint(100_000, 100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        r.register()
        with self.subTest(f'Testing filling update time for Reader {reader_name}'):
            correct_update_time = r.fill_update_time()
            self.assertEqual(correct_update_time, r.get_update_time())

    def test_get_update_time(self):
        reader_name = 'Reader' + str(random.randint(100_000, 100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        r.register()
        with self.subTest(f'Testing getting non-existing update time for Reader {reader_name}'):
            self.assertEqual(None, r.get_update_time())
        correct_update_time = str(r.fill_update_time())
        with self.subTest(f'Testing getting update time for Reader {reader_name}'):
            self.assertEqual(correct_update_time, r.get_update_time())

    def test_delete_read_books(self):
        # 1. Создаем нового читателя
        reader_name = 'Reader' + str(random.randint(100_000, 100_000_000))
        r = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        r.register()

        # 2. Сохраняем для него тестовые книги как прочитанные
        filename = get_correct_filename('sample_books.json', os.path.join(self.test_folder, 'delete_read_books'))
        with open(filename, mode='r', encoding='utf-8') as f:
            books = json.load(f)
        saved_books_num = r._save_read_books_in_db(books)
        r.fill_update_time()

        # 3. Проверяем, что они добавились с помощью save_books_in_db
        with self.subTest('Checking number of saved books'):
            self.assertEqual(len(books), saved_books_num)

        # 4. Проверяем, что они добавились с помощью get_read_books_from_db
        saved_books = r.get_read_books_from_db()
        with self.subTest('Checking number of saved books once more'):
            self.assertEqual(len(books), len(saved_books))

        # 5. Удаляем книги читателя
        r.delete_read_books()

        # 6. Проверяем, что книги удалились
        with self.subTest('Checking that books are deleted'):
            self.assertEqual(0, len(r.get_read_books_from_db()))

    def test_update_books(self):
        # 1. Создаем нового читателя
        # используем реального читателя с небольшим (60) количеством книг
        reader_name = 'Ilaritagli'
        special_config = copy.deepcopy(self.config)
        special_config.web_connection.cache_folder = get_correct_filename('', 'data/sample/test_reader/update_books/cache')
        r = Reader(reader_name, WebWithCache(special_config, random_sleep=True), self.db_connection, self.export)
        print(self.db_connection.filename)
        r.register()
        # 2. Скачиваем книги для него в базу данных
        old_books = r.get_read_books_from_web()
        old_books_num = len(old_books)
        old_update_time = r.get_update_time()
        with self.subTest(f'Checking getting books from web for {reader_name}'):
            self.assertGreater(old_books_num, 0)
        # 3. Обновляем его книги
        print('update books')
        r.update_books()
        # 4. Проверяем, что книги в базе данных есть.
        new_books = r.get_read_books_from_db()
        new_books_num = len(new_books)
        with self.subTest(f'Checking books after update for {reader_name}'):
            self.assertEqual(old_books_num, new_books_num)
        # 5. Проверяем, что время обновления в профиле читателя поменялось
        with self.subTest(f'Checking new update time for {reader_name}'):
            self.assertNotEqual(old_update_time, r.get_update_time())

    def test_get_read_books_from_db(self):
        # 1. Создаем нового читателя
        reader_name = 'Reader' + str(random.randint(100_000, 100_000_000))
        self.object = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        self.object.register()

        # 2. Сохраняем для него тестовые книги как прочитанные
        filename = get_correct_filename('sample_books.json', os.path.join(self.test_folder, 'get_read_books_from_db'))
        with open(filename, mode='r', encoding='utf-8') as f:
            books = json.load(f)
        self.object._save_read_books_in_db(books)
        self.object.fill_update_time()

        # 4. Проверяем, что они добавились с помощью get_read_books_from_db
        saved_books = self.object.get_read_books_from_db()
        with self.subTest('Testing getting books from db'):
            self.process_json_compare_to_json('get_read_books_from_db', 'get_read_books_from_db', 'output', 'input',
                                              False)

        # 5. Удаляем книги читателя
        self.object.delete_read_books()

    def test_get_read_books_from_web(self):
        # 1. Создаем нового читателя
        # используем реального читателя с небольшим (58) количеством книг
        reader_name = 'Humming_Bird'
        # Формируем особый конфиг, чтобы кеш страниц брался из подготовленных данных.
        # Если страница реального читателя поменяется, то сравнение в тесте будет все равно идти с сохраненной старой версией.
        special_config = copy.deepcopy(self.config)
        special_config.web_connection.cache_folder = get_correct_filename('', 'data/sample/test_reader/get_read_books_from_web/cache')
        self.object = Reader(reader_name, WebWithCache(special_config), self.db_connection, self.export)
        # 2. Проверяем работу метода
        self.process_json_compare_to_json('get_read_books_from_web', 'get_read_books_from_web', 'output', 'input',
                                          False)
        # 3. Удаляем книги читателя
        self.object.delete_read_books()

    def test__save_read_books_in_db(self):
        # 1. Создаем нового читателя
        reader_name = 'Reader' + str(random.randint(100_000, 100_000_000))
        self.object = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        self.object.register()

        # 2. Сохраняем для него тестовые книги как прочитанные
        input_filename = get_correct_filename('sample_books.json', os.path.join(self.test_folder, 'save_read_books_in_db'))
        with open(input_filename, mode='r', encoding='utf-8') as f:
            books = json.load(f)
        self.object._save_read_books_in_db(books)
        self.object.fill_update_time()

        # 4. Проверяем, что они добавились с помощью sql запроса
        saved_books = self.db_connection.run_single_sql(
            "SELECT * FROM Book WHERE id in (SELECT book_id FROM ReadBook WHERE reader_id=?)", (self.object.id,))
        output_filename = get_correct_filename('file.json', os.path.join(self.test_folder, 'save_read_books_in_db'))
        with self.subTest("Testing save_read_books_in_db method"):
            with open(output_filename, mode='r', encoding=self.config.encoding) as f:
                correct_output = json.load(f)
                self.assertEqual(saved_books,correct_output)

        # код для обновления файла с правильным ответом
        # with open(output_filename, mode='w', encoding=self.config.encoding) as f:
        #     json.dump(saved_books,f,indent=4,ensure_ascii=False)

        # 5. Удаляем книги читателя
        self.object.delete_read_books()

    def test_register(self):
        # 1. Создаем нового читателя
        reader_name = 'Reader' + str(random.randint(0, 100_000))
        r = Reader(reader_name, self.web_connection, self.db_connection, self.export)
        # 2. Регистрируем его
        r.register()
        # 3. Проверяем, у него теперь ненулевой id
        with self.subTest('Checking not-null id'):
            self.assertGreater(r.id, 0)
        # 4. Проверяем, что он есть в БД
        with self.subTest('Checking new reader is in DB'):
            reader_in_db = self.db_connection.run_single_sql("SELECT * FROM Reader WHERE login=?", (reader_name,))
            # ID должен быть не нулевым
            self.assertNotEqual(0, reader_in_db[0]['id'])
            self.assertEqual(r.id, reader_in_db[0]['id'])
            # Время обновления должно быть None, так как книг еще не загружали.
            self.assertEqual(None, reader_in_db[0]['update_time'])

    def test_get_read_books_from_page(self):
        # 1. Создаем нового читателя
        # используем реального читателя с небольшим (60) количеством книг
        reader_name = 'Kasssiopei'
        # Формируем особый конфиг, чтобы кеш страниц брался из подготовленных данных.
        # Если страница реального читателя поменяется, то сравнение в тесте все равно идти с сохраненной старой версией.
        special_config = copy.deepcopy(self.config)
        special_config.web_connection.cache_folder = get_correct_filename('','data/sample/test_reader/get_read_books_from_page/cache')
        self.object = Reader(reader_name, WebWithCache(special_config), self.db_connection, self.export)
        # 2. Проверяем работу метода
        books = self.object._get_read_books_from_page("/reader/Kasssiopei/read/~0")
        self.process_json_compare_to_json('_get_read_books_from_page', 'get_read_books_from_page', 'output', 'input',
                                          False)

    def test_create_export_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
