import re

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
        # проверяем логин на пустоту или недопустимые символы
        if login != '' and not re.search(r'\W', login):
            # если логин был предоставлен, заменяем им текущий логин читателя
            if login != None:
                self.login = login
            page = self.web_connection.get_page_bs(self.all_books, parser=self.parser_html)
            return True if page else False
        else:
            return False

    def get_all_read_books(self) -> List or bool:
        """
        Возвращает все прочитанные книги читателя
        :return: list or bool
        :rtype: bs4.BeautifulSoup
        """
        result = []
        try:
            # проверяем, есть ли таблица для читателя в БД
            if not self.db_connection.table_exists(self.login):
                self.db_connection.create_table(self.login, BookDataFormatter.all_properties_db())
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
        Сохраняем книги в таблице с именем читателя
        :param books:
        :type books:
        :return:
        :rtype:
        """
        prepared_books = self.parser_db.prepare_books_for_db(books)
        result = self.db_connection.insert_values(self.login, prepared_books)
        return result

    def has_db_entries(self) -> bool:
        pass
