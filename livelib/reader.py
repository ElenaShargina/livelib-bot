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
    :param connection: объект Connection для связи с сайтом
    :type connection: Сonnection
    :param parser_html: класс парсера, который будет применяться к страницам html,
        defaults to Parser
    :type parser_html: cls
    :param parser_db: класс парсера, который будет применяться для работы с БД,
        defaults to ParserForDB
    :type parser_db: cls
    """
    def __init__(self, login: str, connection: WebConnection, dbconnection: DBConnection, parser_html: Parser = ParserFromHTML, parser_db: Parser = ParserForDB):
        self.login = login
        self.connection = connection
        self.parser_html = parser_html
        self.parser_db = parser_db
        self.dbconnection = dbconnection

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

    def get_all_read_books(self) -> List or bool:
        """
        Возвращает все прочитанные книги читателя
        :return: list or bool
        :rtype: bs4.BeautifulSoup
        """
        result = []
        try:
            # проверяем, есть ли таблица для читателя в БД
            if not self.dbconnection.table_exists(self.login):
                self.dbconnection.create_table(self.login, BookDataFormatter.all_properties_db())
            # вызовем первую страницу со всеми книгами, чтобы забрать оттуда из паджинатора список страниц с книгами
            page = self.connection.get_page_bs(self.all_books, self.parser_html)
            page_numbers = self.parser_html.get_paginator(page)
            # если у читателя меньше 20 книг, то паджинатора нет, но есть 1 страница с прочитанным
            if page_numbers == []: page_numbers = [1]
            # формируем список адресов страниц с книгами читателя
            pages = []
            for i in page_numbers:
                pages.append(self.parser_html.reader_read_books_page_by_number(self.login,i))
            for i in pages:
                books = []
                print('page = ',i, ' из ', len(page_numbers))
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
        page = self.connection.get_page_bs(url,self.parser_html)
        if page:
            books = self.parser_html.all_books_from_page(page)
            return books
        else:
            # если страница не найдена либо 404 на ЛЛ
            logging.warning(f'Page with books at {url} is not found or 404.')
            return False

    def save_books_in_db(self, books):
        """
        Сохраняем книги в таблице с именем читателя
        :param books:
        :type books:
        :return:
        :rtype:
        """
        prepared_books = self.parser_db.prepare_books_for_db(books)
        result = self.dbconnection.insert_values(self.login, prepared_books)
        return result