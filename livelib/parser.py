import logging
import re

import bs4
from bs4 import BeautifulSoup as bs
import typing

class DataFormatter:
    pass

class BookDataFormatter(DataFormatter):
    common_properties = {
        'author_id': {'parser': 'get_author_id'},
        'author_name': {'parser': 'get_author_name'},
        'book_id': {'parser':'get_book_id'},
        'book_name': {'parser':'get_book_name'},
        'common_rating': {'parser':'get_common_rating'},
        'picture_url': {'parser':'get_picture_url'}
    }
    reader_properties = {
        'reader_rating': {'parser':'get_reader_rating'},
    }


class ReviewDataFormatter(DataFormatter):
    pass

class ReaderDataFormatter(DataFormatter):
    pass

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
    def all_books_from_page(bsoup, formatter: BookDataFormatter=BookDataFormatter):
        # в коде страницы внутри блока <div id='booklist'></div>
        # чередуются блоки <div class='brow-h2'>Месяц Год</div> и <div class='book-item-manage'>КНИГА</div>
        # последовательно пойдем по этим блокам, присваивая книгам, следующим за датой, эту дату прочтения
        result=[]
        month = None
        year = None
        for block in bsoup.find('div', id='booklist').children:
            # если это блок с месяцем и годом, запоминаем его для добавления в информацию по последующим книгам
            if 'brow-h2' in block['class']:
                date = block.text
                # вытащим месяц, переведем его в цифру
                month = re.search(r'\D+(?= )',date).group()
                month_numbers = {'январь':1, 'февраль':2, 'март':3, 'апрель':4, 'май':5, 'июнь':6,
                                 'июль':7, 'август':8, 'сентябрь':9, 'октябрь':10, 'ноябрь':11, 'декабрь':12}
                month = month_numbers.get(month.lower(),None)
                # вытащим год
                year = re.search(r'\d+', date).group()
            # если это блок с книгой, парсим ее как книгу и вносим месяц и год прочтения в результат
            elif 'book-item-manage' in block['class']:
                book = Parser.book(block, formatter)
                if month: book['month'] = month
                if year: book['year'] = year
                result.append(book)
        return result

    @staticmethod
    def book(bsoup: bs4.BeautifulSoup, formatter: BookDataFormatter=BookDataFormatter):
        result = {}
        for property_name, property_info in dict(formatter.common_properties | formatter.reader_properties).items():
            parser_function = property_info.get('parser', None)
            if parser_function:
                try:
                    result[property_name] = getattr(Parser, parser_function)(bsoup)
                except AttributeError:
                    logging.exception(f'No parser function {parser_function} is found!', exc_info=True)
            else:
                result[property_name] = None

        return result

    @staticmethod
    def get_author_name(bsoup: bs4.BeautifulSoup)->str:
        result = bsoup.find('a', class_='brow-book-author')
        if result and bool(result.text):
            return result.text
        else:
            return None

    @staticmethod
    def get_author_id(bsoup: bs4.BeautifulSoup)->str:
        author_id = re.compile(r'(?<=/author/)\d+(?=-)')
        link = bsoup.find('a', class_='brow-book-author')
        if link:
            result = re.search(author_id,link.get('href'))
            return int(result.group()) if result else None
        else:
            return None

    @staticmethod
    def get_book_name(bsoup: bs4.BeautifulSoup) -> str:
        result = bsoup.find('a', class_='brow-book-name')
        if result and bool(result.text):
            return result.text
        else:
            return None

    @staticmethod
    def get_book_id(bsoup: bs4.BeautifulSoup)->str:
        book_id = re.compile(r'(?<=/book/)\d+(?=-)')
        link = bsoup.find('a', class_='brow-book-name')
        if link:
            result = re.search(book_id,link.get('href'))
            return int(result.group()) if result else None
        else:
            return None

    @staticmethod
    def get_common_rating(bsoup: bs4.BeautifulSoup) -> float:
        result = bsoup.find('div', class_='brow-ratings').find_all('span', class_='rating-book')[1]
        if result and bool(result.text):
            return float(result.text)
        else:
            return None

    @staticmethod
    def get_picture_url(bsoup: bs4.BeautifulSoup) -> str:
        result = bsoup.find('div', class_='cover-wrapper').find('img').get('data-pagespeed-lazy-src')
        if result:
            return result
        else:
            result = bsoup.find('div', class_='cover-wrapper').find('img').get('src')
            return result if result else None

    @staticmethod
    def get_reader_rating(bsoup: bs4.BeautifulSoup) -> float:
        result = bsoup.find('div', class_='brow-ratings').find_all('span', class_='rating-book')[0]
        if result and bool(result.text):
            return float(result.text)
        else:
            return None
