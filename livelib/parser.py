import bs4
from bs4 import BeautifulSoup as bs
import typing

class Parser:
    """
    Класс парсинга страниц сайта. Здесь задаются адресация страниц сайта и поиск данных в его верстке.
    """
    @staticmethod
    def reader_prefix(login: str) -> str:
        """
        Возвращает префикс страниц сайта для конкретного читателя.
        :param login: логин читателя
        :type login: str
        :return: префикс страниц сайта для конкретного читателя
        :rtype: str
        """
        return '/reader/'+login

    @staticmethod
    def reader_all_books(login: str) -> str:
        """
        Возвращает страницу с книгами, прочитанными читателем
        :param login: логин читателя
        :type login: str
        :return: страница с прочитанными книгами
        :rtype: str
        """
        return Parser.reader_prefix(login) + '/read/listview/smalllist'

    @staticmethod
    def check_404(bsoup: bs4.BeautifulSoup) -> bool:
        """
        Проверяет, не возвращает ли страница 404.
        :param bsoup: текст страницы
        :type bsoup:  bs4.BeautifulSoup
        :return: True, если 404, False иначе
        :rtype: Boolean
        """
        if bsoup.find('title', string='404 @ LiveLib'):
            return True
        else:
            return False

    @staticmethod
    def all_books_from_page(bsoup):
        return bsoup.find_all('div', attrs={'class':'book-item-manage'})
