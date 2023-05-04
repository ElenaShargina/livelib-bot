import re

import bs4
from bs4 import BeautifulSoup as bs
from livelib import *
import logging
from typing import Any


class Reader:
    """
    Класс для работы с конкретным пользователем livelib.
    :param login: логин читателя на сайте
    :type login: str
    :param connection: объект Connection для связи с сайтом
    :type connection: Сonnection
    :param bs_parser: класс парсера BeautifulSoup, который будет применяться к страницам,
        defaults to Parser
    :type bs_parser: str
    """
    def __init__(self, login: str, connection: Connection, bs_parser: Any = Parser):
        self.login = login
        self.connection = connection
        self.bsp = bs_parser

    @property
    def prefix(self) -> str:
        """
        Возвращает префикс страниц, относящихся к текущему читателю. Введено для наглядности кода.
        :return: префикс страниц
        :rtype: str
        """
        return self.bsp.reader_prefix(self.login)

    @property
    def all_books(self) -> str:
        """
        Возвращает префикс главной страницы, относящихся к текущему читателю. Введено для наглядности кода.
        :return: префикс главной страницы
        :rtype: str
        """
        return self.bsp.reader_all_books(self.login)

    def get_read_books_main_page(self) -> bs4.BeautifulSoup:
        """
        Возвращает главную страницу читателя
        :return: главная страница читателя
        :rtype: bs4.BeautifulSoup
        """
        try:
            page = self.connection.get_page_bs_check_404(self.all_books, self.bsp)
        except Exception:
            logging.exception(f'The page with read books for reader {self.login} is not found! ', exc_info=True)

    # def get_books_from_page(self, url):
    #     page = self.connection.get_page(url)
    #     if page != None:
    #         bs_page = bs(page, self.connection.bs_parser)
    #         all_books = bs_page.find_all('div', attrs={'class':'book-item-manage'})
    #         print(all_books)
    #         res = [book.find('a', attrs={'class':'brow-book-name'}).text for book in all_books]
    #         return res
    #
    # def get_all_books(self):
    #     page = self.connection.get_page(self.all_books)
    #     # @todo рассмотреть другие случаи
    #     if page != None:
    #         bs_page = bs(page, self.connection.bs_parser)
    #         last_page_url = bs_page.find('div', attrs={'id':'booklist-pagination'}).find('span', attrs={'class':'i-pager-last'}).find_parent('a')['href']
    #         # @todo проверить правильность регулярного выражения
    #         last_page = re.search(r'\d+$',last_page_url).group()
    #         print(last_page)
    #         book_list_pages = []
    #         for i in range(int(last_page)):
    #             book_list_pages.append(f'{self.prefix}/read/listview/smalllist/~{i}')
    #
    #         for url in book_list_pages:
    #             print(url)
    #             print(self.get_books_from_page(url))
