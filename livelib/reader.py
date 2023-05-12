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
                 parser_html: type[Parser] = ParserFromHTML,
                 parser_db: type[Parser] = ParserForDB):
        self.login = login
        self.web_connection = web_connection
        self.object_html = parser_html
        self.object_db = parser_db
        self.db_connection = db_connection
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
    def all_books(self) -> str:
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
            page = self.web_connection.get_page_bs(self.all_books, parser=self.parser_html)
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
        if result != []:
            result = result[0].get('update_time', None)
        else:
            result = None
        return result

    def insert_into_db(self) -> int:
        """
        Добавляет читателя в базу данных и возвращает его ID.
        Если читатель уже есть в БД, то возвращает старый ID, не добавляя снова.
        :return:
        :rtype: int
        """
        # на всякий случай проверяем, нет ли пользователя с тем же логином
        old_id = self.get_db_id()
        if not old_id:
            self.db_connection.run_single_sql("INSERT INTO Reader (login) VALUES (?)", (self.login,))
            result = self.get_db_id()
            logging.info(f'Adding new Reader to DB: {self.login} at id = {result}')
            return result
        else:
            return old_id

    def get_db_id(self) -> bool:
        """
        Возвращает ID читателя из БД. Если такого читателя нет, возвращает None
        :return:
        :rtype:
        """
        result = self.db_connection.run_single_sql("SELECT * FROM Reader WHERE login = ?",(self.login,))
        if len(result)>0:
            return result[0].get('id', None)
        else:
            return None

    def register(self):
        """
        Регистрация читателя в базе данных и запоминание его id
        """
        self.id = self.insert_into_db()

    def get_all_read_books(self) -> List or bool:
        """
        Возвращает все прочитанные книги читателя
        :return: list or bool
        :rtype: bs4.BeautifulSoup
        """
        result = []
        try:
            # вызовем первую страницу со всеми книгами, чтобы забрать оттуда из паджинатора список страниц с книгами
            page = self.web_connection.get_page_bs(self.all_books, self.parser_html)
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
                    books = self.get_books_from_page(i)
                    print(books)
                    num = self.save_books_in_db(books)
                    print(f'Saving {num} books to DB')
                    logging.info(f'Saving {num} books to DB')
                except Exception:
                    logging.exception(f'Read books for reader {self.login}  at {i} is not found! ', exc_info=True)
                result = result + books
            return result
        except Exception:
            logging.exception(f'The page with read books for reader {self.login} is not found! ', exc_info=True)
            return False

    def get_books_from_page(self, url: str) -> List or bool:
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
            logging.warning(f'Page with books at {url} is not found or 404.')
            return False



    def save_books_in_db(self, books : list[dict]):
        """
        Сохраняем книги в БД
        :param books:
        :type books:
        :return:
        :rtype:
        """
        prepared_books = self.parser_db.prepare_books_for_db(books)
        print(books)
        book_properties = BookDataFormatter.book_properties_db
        print(book_properties)
        for book in books:
            result = self.db_connection.insert_values('Book', [{key:book[key] for key in book_properties},])
        return result

    def update_books(self):
        pass

    def download_books(self):
        pass

    def create_export_file(self, type = 'csv'):
        pass
