import datetime
import re
import typing


import bs4
from bs4 import BeautifulSoup as bs
from livelib import *
import logging
from typing import Any, List
import random
import time
from .dbconnection import DBConnection
from .parser import BookDataFormatter
from .export import Export


class Reader:
    """
    Класс для работы с конкретным пользователем livelib.
    :param login: логин читателя на сайте
    :type login: str
    :param web_connection: объект Connection для связи с сайтом
    :type web_connection: Сonnection
    :param parser_html: класс парсера, который будет применяться к страницам html,
        defaults to Parser
    :type parser_html: cls
    :param parser_db: класс парсера, который будет применяться для работы с БД,
        defaults to ParserForDB
    :type parser_db: cls
    """

    def __init__(self,
                 login: str,
                 web_connection: WebConnection,
                 db_connection: DBConnection,
                 export: Export,
                 parser_html: type[Parser] = ParserFromHTML,
                 parser_db: type[Parser] = ParserForDB):
        self.login = login
        self.web_connection = web_connection
        self.db_connection = db_connection
        self.export = export
        self.parser_html = parser_html
        self.parser_db = parser_db

        self.id = None

    @property
    def prefix(self) -> str:
        """
        Возвращает префикс страниц, относящихся к текущему читателю. Введено для наглядности кода.
        :return: префикс страниц
        :rtype: str
        """
        return self.parser_html.reader_prefix(self.login)

    @property
    def all_books_page(self) -> str:
        """
        Возвращает префикс главной страницы, относящихся к текущему читателю. Введено для наглядности кода.
        :return: префикс главной страницы
        :rtype: str
        """
        return self.parser_html.reader_read_books_page(self.login)

    def exists(self, login: str = None) -> bool:
        """
        Проверяет на существование такой логин на сайте ЛЛ и помещает этот логин в текущий объект.
        :param login: логин из букв латинского алфавита и нижних подчеркиваний
        :type login: str
        :return:
        :rtype: bool
        """
        if login == None: login = self.login
        # проверяем логин на пустоту или недопустимые символы
        if login != '' and not re.search(r'\W', login):
            # если логин был предоставлен, заменяем им текущий логин читателя
            if login != None:
                self.login = login
            page = self.web_connection.get_page_bs(self.all_books_page, parser=self.parser_html)
            return True if page else False
        else:
            return False

    def has_db_entries(self) -> typing.Optional[str]:
        """
        Возвращает либо дату последнего обновления пользователя в БД,
                    либо None, если пользователь не существует,
                                или обновлений не было.
        """
        result = self.db_connection.run_single_sql(f'SELECT * FROM Reader WHERE login=?', (self.login,))
        if result:
            result = result[0].get('update_time', None)
        else:
            result = None
        return result

    def get_db_id(self) -> bool:
        """
        Возвращает ID читателя из БД. Если такого читателя нет, возвращает None
        :return:
        :rtype:
        """
        result = self.db_connection.run_single_sql("SELECT * FROM Reader WHERE login = ?",(self.login,))
        if result:
            return result[0].get('id', None)
        else:
            return None

    def insert_into_db(self) -> int:
        """
        Добавляет читателя в базу данных и возвращает его ID.
        Если читатель уже есть в БД, то возвращает старый ID, не добавляя снова.
        :return:
        :rtype: int
        """
        # на всякий случай проверяем, нет ли пользователя с тем же логином
        old_id = self.get_db_id()
        if old_id == None:
            result = self.db_connection.run_single_sql("INSERT INTO Reader (login) VALUES (?)", (self.login,), return_lastrowid=True)
            logging.info(f'Adding new Reader to DB: {self.login} at id = {result}')
            return result
        else:
            return old_id

    def register(self):
        """
        Регистрация читателя в базе данных и запоминание его id
        """
        self.id = self.insert_into_db()

    def get_read_books_from_web(self) -> List or bool:
        """
        Загружает все прочитанные книги читателя из сети (через WebConnection) в базу данных (через BDConnection)
        :return: список со словарями книг
        :rtype: list or bool
        """
        result = []
        try:
            # вызовем первую страницу со всеми книгами, чтобы забрать оттуда из паджинатора список страниц с книгами
            page = self.web_connection.get_page_bs(self.all_books_page, self.parser_html)
            page_numbers = self.parser_html.get_paginator(page)
            # если у читателя меньше 20 книг, то паджинатора нет, но есть 1 страница с прочитанным
            if page_numbers == []: page_numbers = [1]
            # формируем список адресов страниц с книгами читателя
            pages = []
            for i in page_numbers:
                pages.append(self.parser_html.reader_read_books_page_by_number(self.login, i))
            for i in pages:
                books = []
                print('page = ', i, ' из ', len(page_numbers))
                try:
                    books = self.get_read_books_from_page(i)
                    # print(books)
                    # сохраняем порцию книг в базе данных
                    num = self.save_read_books_in_db(books)
                    print(f'Saving {num} books to DB')
                    logging.info(f'Saving {num} books to DB')
                except Exception:
                    logging.exception(f'Error while getting and saving portion of books for reader {self.login}  at page {i}  .', exc_info=True)
                result = result + books
            # помечаем время последнего обновления книг в таблице читателей
            self.fill_update_time()
            return result
        except Exception:
            logging.exception(f'The page with read books for reader {self.login} is not found! ', exc_info=True)
            return False

    def get_read_books_from_page(self, url: str) -> List or bool:
        """
        Получает список книг с заданной страницы
        :param url: адрес страницы
        :type url: str
        :return: список книг либо False, если страница не найдена
        :rtype: list or bool
        """
        page = self.web_connection.get_page_bs(url, self.parser_html)
        if page:
            books = self.parser_html.all_books_from_page(page)
            return books
        else:
            # если страница не найдена либо 404 на ЛЛ
            logging.warning(f'Page with books at {url} is not found or 404, or captcha.')
            return False

    def save_read_books_in_db(self, books : list[dict]):
        """
        Сохраняем книги в БД
        :param books:
        :type books:
        :return:
        :rtype:
        """
        prepared_books = self.parser_db.prepare_books_for_db(books)
        # сохраняем книги в таблице Book
        book_properties = BookDataFormatter.book_properties_db
        # print('всего книг ',len(books))

        for book in books:
            self.db_connection.insert_values('Book', [{key:book[key] for key in book_properties},])
        # сохраняем связи между читателем и книгами в таблице ReadBook вместе с его оценкой и рецензией
        # узнаем id добавленных книг
        new_books = [book['book_id'] for book in books if book['book_id']]
        new_works = [book['work_id'] for book in books if book['work_id']]
        # print('всего books ', len(new_books))
        # print('всего works ', len(new_works))
        new_ids = self.db_connection.run_single_sql(f"SELECT id, book_id, work_id FROM Book where book_id in ({','.join(['?']*len(new_books))})"
                                                    f" OR work_id in ({','.join(['?']*len(new_works))}) ",
                                                    new_books+new_works)
        # print('всего new_ids ', len(new_ids))
        # разбираем новые id, формируем список строк для занесения в ReadBook
        readbook_rows = []
        readbook_properties = BookDataFormatter.readbook_properties_db
        for i in new_ids:
            # находим соответствующую запись в общем массиве books
            if i['book_id']:
                entry = [item for item in books if item['book_id']==i['book_id']][0]
            elif i['work_id']:
                entry = [item for item in books if item['work_id']==i['work_id']][0]
            # добавляем в новую запись нужные для таблицы свойства
            new_entry = {key:value for key,value in entry.items() if key in readbook_properties}
            new_entry['reader_id'] = self.id
            new_entry['book_id'] = i['id']
            readbook_rows.append(new_entry)
        # добавляем новые значения в таблицу ReadBook
        result = self.db_connection.insert_values('ReadBook', readbook_rows)
        logging.info(f'Added new {result} entries to ReadBook for Reader {self.id} {self.login}')
        return result

    def fill_update_time(self) -> str:
        """
        Помечает в БД, что данные читателя обновлены сейчас.
        Возвращает строковое представление вставленного времени формата '2023-05-13 10:14:10.121082'
        :return:
        :rtype: str
        """
        new_time = datetime.datetime.now()
        self.db_connection.run_single_sql("UPDATE Reader SET update_time=? WHERE login=?", (new_time, self.login,))
        logging.info(f'Filling update_time of Reader {self.login} to {new_time}')
        return str(new_time)

    def get_update_time(self) -> str or None:
        """
        Возвращает дату последнего обновления данных читателя в строковом формате '2023-05-13 10:14:10.121082' или None,
        если данные еще не вносились/обновлялись.
        :return:
        :rtype:
        """
        result = self.db_connection.run_single_sql("SELECT update_time FROM Reader WHERE login=?", (self.login,))
        if result:
            return result[0]['update_time']
        else:
            return None

    def delete_read_books(self):
        """
        Удаляет прочитанные книги читателем из таблицы ReadBook. В Book они сохраняются.
        """
        # удаляем связи читателя с книгами в таблице ReadBook
        self.db_connection.run_single_sql("DELETE FROM ReadBook WHERE reader_id=?", (self.id,))
        logging.info(f'Delete read books for Reader {self.id} {self.login}')

    def get_read_books_from_db(self) -> list:
        """
        Возвращает книги, прочитанные читателем, из БД.
        :return:
        :rtype: list[dict]
        """
        result = self.db_connection.run_single_sql("SELECT * FROM Book INNER JOIN ReadBook ON Book.id=ReadBook.book_id WHERE ReadBook.reader_id=?", (self.id,))
        # нужно удалить reader_id  и id из полученного ответа
        # для прохождения юнит тестов с динамически генерируемыми пользователями
        for i in result:
            del i["reader_id"]
            del i["id"]
        return result

    def update_books(self):
        """
        Обновляет прочитанные читателем книги в БД. Удаляет все связи книг и читателя в ReadBook, затем скачивает из сети новые.
        """
        self.delete_read_books()
        self.get_read_books_from_web()

    def create_export_xlsx_file(self):
        books = self.get_read_books_from_db()
        print(len(books))
        print(self.login)
        f = self.export.create_file(books = books, login = self.login)
        return f