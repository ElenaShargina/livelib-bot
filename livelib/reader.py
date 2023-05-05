import re

import bs4
from bs4 import BeautifulSoup as bs
from livelib import *
import logging
from typing import Any, List
import random
import time

class Reader:
    """
    Класс для работы с конкретным пользователем livelib.
    :param login: логин читателя на сайте
    :type login: str
    :param connection: объект Connection для связи с сайтом
    :type connection: Сonnection
    :param bs_parser: класс парсера, который будет применяться к страницам,
        defaults to Parser
    :type bs_parser: str
    """
    def __init__(self, login: str, connection: Connection, parser: Any = Parser):
        self.login = login
        self.connection = connection
        self.parser = parser

    @property
    def prefix(self) -> str:
        """
        Возвращает префикс страниц, относящихся к текущему читателю. Введено для наглядности кода.
        :return: префикс страниц
        :rtype: str
        """
        return self.parser.reader_prefix(self.login)

    @property
    def all_books(self) -> str:
        """
        Возвращает префикс главной страницы, относящихся к текущему читателю. Введено для наглядности кода.
        :return: префикс главной страницы
        :rtype: str
        """
        return self.parser.reader_all_books(self.login)

    def get_all_read_books(self) -> List or bool:
        """
        Возвращает все прочитанные книги читателя
        :return: list or bool
        :rtype: bs4.BeautifulSoup
        """
        try:
            # вызовем первую страницу со всеми книгами, чтобы забрать оттуда из паджинатора список страниц с книгами
            page = self.connection.get_page_bs(self.all_books, self.parser)
            page_numbers = self.parser.get_paginator(page)
            print(page_numbers)
            # если у читателя меньше 20 книг, то паджинатора нет, но есть 1 страница с прочитанным
            if page_numbers == []: page_numbers = [1]
            pages = []
            for i in page_numbers:
                pages.append(self.parser.reader_read_books_page_by_number(self.login,i))
            print(pages)
            for i in pages:
                print(i)
                try:
                    books = self.get_books_from_page(i)
                except Exception as exc:
                    logging.exception(f'Read books for reader {self.login}  at {i} is not found! ', exc_info=True)
                print(f'page={i}, {len(books)} parsed')
                print(books[0])
            return []
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
        page = self.connection.get_page_bs(url,self.parser)
        if page:
            books = self.parser.all_books_from_page(page)
            return books
        else:
            # если страница не найдена либо 404 на ЛЛ
            logging.warning(f'Page with books at {url} is not found or 404.')
            return False
