import logging
import re

import bs4
from bs4 import BeautifulSoup as bs
import typing
from typing import List, Dict

class DataFormatter:
    pass

class BookDataFormatter(DataFormatter):
    common = {
        'author_id': {'parser': 'get_author_id', 'db': {'name':'author_id', 'type': 'INTEGER'}},
        'author_name': {'parser': 'get_author_name', 'db': {'name':'author_name', 'type': 'TEXT'}},
        'book_id': {'parser':'get_book_id', 'db': {'name':'book_id', 'type': 'INTEGER'}},
        'work_id': {'parser': 'get_work_id', 'db': {'name': 'work_id', 'type': 'INTEGER'}},
        'book_name': {'parser':'get_book_name', 'db': {'name':'book_name', 'type': 'TEXT'}},
        'common_rating': {'parser':'get_common_rating', 'db': {'name':'common_rating', 'type': 'REAL'}},
        'picture_url': {'parser':'get_picture_url', 'db': {'name':'picture_url', 'type': 'TEXT'}},
    }
    reader = {
        'reader_rating': {'parser':'get_reader_rating', 'db': {'name':'reader_rating', 'type': 'REAL'}},
        'tags': {'parser': 'get_tags', 'db': {'name':'tags', 'type': 'TEXT'}}
    }

    @classmethod
    def common_parser(cls):
        """
        :return: словарь вида {название_поля: метод_его_обработки, ..:.., }
        :rtype: Dict
        """
        return {i:j['parser'] for i,j in cls.common.items()}

    @classmethod
    def common_db(cls):
        """
        :return: список вида [{название_поля_в_БД: тип_поля_в_БД},{}]
        :rtype: List
        """
        return [i['db'] for i in cls.common.values()]

    @classmethod
    def reader_parser(cls):
        """
        :return: словарь вида {название_поля: метод_его_обработки}
        :rtype: Dict
        """
        return {i:j['parser'] for i,j in cls.reader.items()}

    @classmethod
    def reader_db(cls):
        """
        :return: список вида (название_поля_в_БД: тип_поля_в_БД )
        :rtype: List
        """
        return [i['db'] for i in cls.reader.values()]


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
    def reader_read_books_page_by_number(login:str, number:int) -> str:
        """
        Возвращает страницу с книгами, прочитанными читателем
        :param login: логин читателя
        :type login: str
        :return: страница с прочитанными книгами
        :rtype: str
        """
        return Parser.reader_prefix(login)+'/read/~'+str(number)

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
    def all_books_from_page(bsoup: bs4.BeautifulSoup, formatter: BookDataFormatter=BookDataFormatter) -> List[Dict]:
        """
        Возвращает ифнормацию о всех книгах на данной странице в виде списка словарей.
        Словарь формируется с ключами из BookDataFormatter, соответствующие значения вычисляются
        с помощью функций, указанных там же.
        Исключение - месяц и год прочтения книги формируются в этом методе, это обусловлено версткой.
        :param bsoup: код страницы
        :type bsoup: bs4.BeautifulSoup
        :param formatter:  словарь с перечислением нужных свойств
        :type formatter: BookDataFormatter
        :return: список словарей по каждой книге вида {'property_name': 'property_value'}
        :rtype: List[Dict]
        """
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
                # вытащим месяц (если он есть, для старых книг его может не быть), переведем его в цифру
                month = re.search(r'\D+(?= )',date)
                if month != None:
                    month = month.group()
                    month_numbers = {'январь':1, 'февраль':2, 'март':3, 'апрель':4, 'май':5, 'июнь':6,
                                 'июль':7, 'август':8, 'сентябрь':9, 'октябрь':10, 'ноябрь':11, 'декабрь':12}
                    month = month_numbers.get(month.lower(),None)
                # вытащим год
                year = re.search(r'\d+', date)
                if year != None: year = year.group()
            # если это блок с книгой, парсим ее как книгу и вносим месяц и год прочтения в результат
            elif 'book-item-manage' in block['class']:
                book = Parser.book(block, formatter)
                if month: book['month'] = month
                if year: book['year'] = year
                result.append(book)
        return result

    @staticmethod
    def book(bsoup: bs4.BeautifulSoup, formatter: BookDataFormatter=BookDataFormatter) -> Dict[str,str]:
        """
        Возвращает словарь с информацией о книге, представленной в заданном коде.
        Словарь формируется с ключами из BookDataFormatter, соответствующие значения вычисляются
        с помощью функций, указанных там же.
        Исключение - месяц и год прочтения книги формируются в методе all_books_from_page, это обусловлено версткой.
        :param bsoup: код с информацией о книге
        :type bsoup: bs4.BeautifulSoup
        :param formatter: словарь с перечислением нужных свойств
        :type formatter: BookDataFormatter
        :return: словарь типа {'property_name': 'property_value'}
        :rtype: Dict[str,str]
        """
        result = {}
        for property_name, parser_function in dict(formatter.common_parser() | formatter.reader_parser()).items():
                try:
                    result[property_name] = getattr(Parser, parser_function)(bsoup)
                except AttributeError:
                    logging.exception(f'No parser function {parser_function} is found!', exc_info=True)
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
    def get_work_id(bsoup: bs4.BeautifulSoup)->str:
        book_id = re.compile(r'(?<=/work/)\d+(?=-)')
        link = bsoup.find('a', class_='brow-book-name')
        if link:
            result = re.search(book_id,link.get('href'))
            return int(result.group()) if result else None
        else:
            return None

    @staticmethod
    def get_common_rating(bsoup: bs4.BeautifulSoup) -> float:
        """
        Возвращает общую оценку книги.
        :param bsoup: код, вмещающий информацию о книге
        :type bsoup: bs4.BeautifulSoup
        :return: число
        :rtype: float
        """
        result = bsoup.find('div', class_='brow-ratings').find_all('span', class_='rating-book')[1]
        if result and bool(result.text):
            return float(result.text)
        else:
            return None

    @staticmethod
    def get_picture_url(bsoup: bs4.BeautifulSoup) -> str:
        """
        Возвращает ссылку на картинку с обложкой книги.
        :param bsoup: код, вмещающий информацию о книге
        :type bsoup: bs4.BeautifulSoup
        :return: абсолютную ссылку
        :rtype: str
        """
        result = bsoup.find('div', class_='cover-wrapper').find('img').get('data-pagespeed-lazy-src')
        if result:
            return result
        else:
            result = bsoup.find('div', class_='cover-wrapper').find('img').get('src')
            return result if result else None

    @staticmethod
    def get_reader_rating(bsoup: bs4.BeautifulSoup) -> float:
        """
        Возвращает оценку книги читателем.
        :param bsoup: код, вмещающий информацию о книге
        :type bsoup: bs4.BeautifulSoup
        :return: число
        :rtype: float
        """
        result = bsoup.find('div', class_='brow-ratings').find_all('span', class_='rating-book')[0]
        if result and bool(result.text):
            return float(result.text)
        else:
            return None

    @staticmethod
    def get_tags(bsoup: bs4.BeautifulSoup):
        tags = bsoup.find('div', class_='brow-tags')
        result = []
        if tags != None:
            # необходимо проверить, не является ли тег ссылкой на расширенный список тегов (вида 'Еще NN тегов')
            # Если он - ссылка, то пропускаем его.
            # даже если теги скрыты, мы все равно их вытащим из кода страницы.
            more = re.compile(r'^Ещё \d+')
            for i in tags.find_all('a', class_='label-tag'):
                if re.match(more, i.text)==None:
                    result.append(i.text)
        return ' '.join(result)

    @staticmethod
    def get_paginator(bsoup: bs4.BeautifulSoup) -> List[int]:
        """
        Возвращает список номеров страниц из паджинатора в низу страницы. Если страница единственная, и паджинатора нет,
        то возвращает пустой список.
        :param bsoup: код страницы
        :type bsoup: bs4.BeautifulSoup
        :return: список номеров страниц либо пустой список
        :rtype: List[int]
        """
        paginator = bsoup.find('div', id='booklist-pagination')
        result = []
        # если страница единственная, она же текущая, то возвращаем пустой список ссылок
        if paginator == None:
            return result
        # если страницы есть
        else:
            last_page = paginator.find('a', title='Последняя страница')
            # если не все страницы представлены, но есть ссылка на самую последнюю страницу
            if last_page:
                last_number = int(re.search(r'(?<=~)\d+',last_page['href']).group())
                result = [i for i in range(1,last_number+1)]
            # если все страницы умещаются в низу страницы (их мало, до пяти штук)
            else:
                result = [int(i) for i in paginator.text.split()]
            return result

    @staticmethod
    def prepare_books_for_db(books:List[Dict], formatter = BookDataFormatter) -> List:
        """
        Преобразует список книг для сохранения в БД в соответствии с BookDataFormatter.
        Нужен в случае, если название колонки в БД отличается от названия свойства парсера и
        в таблицу с книгами не сохраняются такие свойства книг как теги, оценка читателя и рецензия.
        :param books: список книг вида [{'parser_field_name1':'field_value1','parser_field_name2':'field_value2'},{}]
        :type books: List[Dict]
        :param formatter: класс форматтера
        :type formatter: Class
        :return: список для сохранения  в БД вида [{'db_field_name1':'field_value1', 'db_field_name2':'field_value2'}, {}]
        :rtype: List[Dict]
        """
        result = []
        for book in books:
            new_book = {}
            for property in formatter.common.keys():
                value = book.get(property, None)
                if value == None: value = ''
                new_book[formatter.common[property]['db']['name']] = value
            result.append(new_book)
        return result
