import logging
import os
import re

import bs4
from bs4 import BeautifulSoup as bs
import typing
from typing import List, Dict
from datetime import datetime


class DataFormatter:
    pass


class BookDataFormatter(DataFormatter):
    """
    Класс содержит таблицу соответствий между свойствами книги в БД, в колонках экспортного файла
    и методами парсера (класса ParserFromHTML), вынимающими это свойство из html.
    {
    'название_свойства': {
           'parser': 'метод_для_вынимания_свойства_из_html_кода',
           'db': { 'name': 'название_колонки_в_бд',
                    'type': 'тип_колонки_в_бд'
                    },
           'csv': { 'name': 'Название_колонки_в_csv',
                    'method': 'метод_для_форматирования_значения_для_csv'
                    },
            'xlsx': {   'name': 'Название_колонки_в_xlsx',
                        'method': 'метод_для_форматирования_значения_для_xlsx',
                        'order': 'порядок следования в таблице в формате integer'
                    }
           },
    ...
    }
          свойства date, month, year не вынимаются из html стандартным способом,
          поэтому его parser не задан. Они будут вынуты в методе ParserFromHTML.all_books_from_page()

          На ЛЛ есть книги со ссылкой вида /book/book_id и произведения со ссылкой вида /work/work_id.
    """

    common = {
        'author_id': {'parser': 'get_author_id',
                      'db': {'name': 'author_id', 'type': 'INTEGER'},
                      'csv': {'name': 'Cсылка на автора', 'method': 'create_author_link'},
                      'xlsx': {'name': 'Cсылка на автора', 'method': 'create_author_link', 'order' :11},
                      },
        'author_name': {'parser': 'get_author_name',
                        'db': {'name': 'author_name', 'type': 'TEXT'},
                        'csv': {'name': 'Автор', },
                        'xlsx': {'name': 'Автор', 'order':2 }
                        },
        'book_id': {'parser': 'get_book_id',
                    'db': {'name': 'book_id', 'type': 'INTEGER'},
                    'csv': {'name': 'Ссылка на  книгу', 'method': 'create_book_link'},
                    'xlsx': {'name': 'Ссылка на  книгу', 'method': 'create_book_link', 'order':10}
                    },
        'work_id': {'parser': 'get_work_id',
                    'db': {'name': 'work_id', 'type': 'INTEGER'},
                    'csv': {'name': 'Ссылка на произведение', 'method': 'create_work_link'},
                    'xlsx': {'name': 'Ссылка на произведение', 'method': 'create_work_link','order':11}
                    },
        'book_name': {'parser': 'get_book_name',
                      'db': {'name': 'book_name', 'type': 'TEXT'},
                      'csv': {'name': 'Название', },
                      'xlsx': {'name': 'Название', 'order':1}
                      },
        'common_rating': {'parser': 'get_common_rating',
                          'db': {'name': 'common_rating', 'type': 'REAL'},
                          'csv': {'name': 'Общая оценка', },
                          'xlsx': {'name': 'Общая оценка', 'order':9}
                          },
        'picture_url': {'parser': 'get_picture_url',
                        'db': {'name': 'picture_url', 'type': 'TEXT'},
                        'csv': {'name': 'Обложка', 'method': 'create_picture_url'},
                        'xlsx': {'name': 'Обложка', 'method': 'create_picture_url', 'order':3}
                        },
        'reader_rating': {'parser': 'get_reader_rating',
                          'db': {'name': 'reader_rating', 'type': 'REAL'},
                          'csv': {'name': 'Моя оценка', },
                          'xlsx': {'name': 'Моя оценка', 'order':4 }
                          },
        'tags': {'parser': 'get_tags',
                 'db': {'name': 'tags', 'type': 'TEXT'},
                 'csv': {'name': 'Теги', },
                 'xlsx': {'name': 'Теги', 'order':7}
                 },
        'review_id': {'parser': 'get_review_id',
                      'db': {'name': 'review_id', 'type': 'INTEGER'},
                      'csv': {'name': 'Ссылка на рецензию', 'method': 'create_review_link'},
                      'xlsx': {'name': 'Ссылка на рецензию', 'method': 'create_review_link', 'order':6},
                      },
        'review_text': {'parser': 'get_review_text',
                        'db': {'name': 'review_text', 'type': 'TEXT'},
                        'csv': {'name': 'Рецензия', 'method': 'create_rexiew_text'},
                        'xlsx': {'name': 'Рецензия', 'method': 'create_rexiew_text', 'order':5}
                        },
        'date': {'parser': 'not_implemented',
                 'csv': {'name': 'Дата прочтения', },
                 'xlsx': {'name': 'Дата прочтения', 'order':8}
                 },
        'month': {'parser': 'not_implemented',
                  'db': {'name': 'month', 'type': 'INTEGER'},
                  },
        'year': {'parser': 'not_implemented',
                 'db': {'name': 'year', 'type': 'INTEGER'},
                 },
        'livelib_id': {'parser': 'not_implemented',
                       'db': {'name': 'livelib_id', 'type': 'INTEGER'},
                       },
        'login': {'parser': 'not_implemented',
                  'db': {'name': 'login', 'type': 'TEXT'},
                  },
        'update_time': {'parser': 'not_implemented',
                        'db': {'name': 'update_time', 'type': 'TEXT'},
                        },
    }

    book_properties_db = ['book_id', 'work_id', 'book_name', 'author_name', 'author_id', 'common_rating', 'picture_url']
    reader_properties_db = ['livelib_id', 'login', 'update_time']
    readbook_properties_db = ['review_text', 'review_id', 'tags', 'reader_rating', 'month', 'year']

    @classmethod
    def all_properties_parser(cls):
        """
        Преобразует таблицу в удобный для ParserFromHTML словарь.
        :return: словарь вида {название_поля1: метод_обработки_поля1, название_поля2: метод_обработки_поля2, }
        :rtype: Dict
        """
        return {i: j['parser'] for i, j in cls.common.items()}

    @classmethod
    def all_properties_db(cls):
        """
        Преобразует таблицу в удобный для DBConnection словарь.
        :return: словарь вида {'название_поля1':'тип_обработки_поля1', 'название_поля2':'тип_обработки_поля1', ...}
        :rtype: Dict
        """
        result = {}
        for i in cls.common.values():
            if i.get('db'):
                result[i['db']['name']] = i['db']['type']
        return result

    @classmethod
    def all_properties_csv(cls):
        """
        Преобразует таблицу в удобный для CSVConnection словарь
        :return: словарь вида {'author_id': {'name': 'Cсылка на автора', 'method': 'create_author_link'}, {}, ...}
        :rtype: Dict
        """
        result = {}
        for i, j in cls.common.items():
            if j.get('csv'):
                result[i] = j['csv']
        return result

    @classmethod
    def all_properties_xlsx(cls):
        """
        Преобразует таблицу в удобный для XLSXConnection словарь, упорядоченный по заданному порядку
        :return: Словарь вида {'author_id': {'name': 'Cсылка на автора', 'method': 'create_author_link'}, {}, ...}
        :rtype: Dict
        """
        result = {}
        for i, j in cls.common.items():
            if j.get('xlsx'):
                result[i] = j['xlsx']
        sorted_result ={i[0]:i[1] for i in sorted(result.items(), key=lambda x: x[1]['order'])}
        return sorted_result


class Parser:

    @staticmethod
    def _clear_name(s: str) -> str:
        """
        Служебная функция для очистки названий от переносов и лишних пробелов
        """
        s = re.sub(" +", " ", s)
        s = re.sub("\n", "", s)
        return s

    @staticmethod
    def create_filepath_csv(login: str) -> str:
        """
        Возвращает путь и безопасное имя файла CSV формата 'login-YYYY-MM-DD--HH-MM-SS.csv'.
        Из логина читателя будут удалены небезопасные символы.
        :param login: логин читателя
        :type login: str
        :return:
        :rtype: str
        """
        login = login.translate(str.maketrans('', '', '\/:*?"<>|'))
        filename = login + "-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + '.csv'
        # @todo тут должна задаваться папка для сохранения csv
        return (os.path.join('csv', filename))


class ParserFromHTML(Parser):
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
        return '/reader/' + login

    @staticmethod
    def reader_read_books_page(login: str) -> str:
        """
        Возвращает начальную страницу с книгами, прочитанными читателем
        :param login: логин читателя
        :type login: str
        :return: страница с прочитанными книгами
        :rtype: str
        """
        return ParserFromHTML.reader_read_books_page_by_number(login=login, number=0)

    @staticmethod
    def reader_read_books_page_by_number(login: str, number: int = 0) -> str:
        """
        Возвращает страницу с заданным номером с книгами, прочитанными читателем
        :param login: логин читателя
        :type login: str
        :param number: номер страницы
        :type number: int
        :return: страница с прочитанными книгами
        :rtype: str
        """
        return ParserFromHTML.reader_prefix(login) + '/read/~' + str(number)

    @staticmethod
    def check_404(bsoup: bs4.BeautifulSoup) -> bool:
        """
        Проверяет, не возвращает ли страница штатные 404.
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
    def check_captcha(bsoup: bs4.BeautifulSoup) -> bool:
        """
        Проверяет, не возвращает ли страница капчу на проверку ботов.
        :param bsoup: текст страницы
        :type bsoup:  bs4.BeautifulSoup
        :return: True, если капча, False иначе
        :rtype: Boolean
        """
        if bsoup.find(string='Please confirm that you and not a robot are sending requests'):
            return True
        else:
            return False

    @staticmethod
    def all_books_from_page(bsoup: bs4.BeautifulSoup, formatter: BookDataFormatter = BookDataFormatter) -> List[Dict]:
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
        result = []
        month = None
        year = None
        for block in bsoup.find('div', id='booklist').children:
            # если это блок с месяцем и годом, запоминаем его для добавления в информацию по последующим книгам
            if 'brow-h2' in block['class']:
                date = block.text
                # вытащим месяц (если он есть, для старых книг его может не быть), переведем его в цифру
                month = re.search(r'\D+(?= )', date)
                if month != None:
                    month = month.group()
                    month_numbers = {'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4, 'май': 5, 'июнь': 6,
                                     'июль': 7, 'август': 8, 'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12}
                    month = month_numbers.get(month.lower(), None)
                # вытащим год
                year = re.search(r'\d+', date)
                if year != None: year = int(year.group())
            # если это блок с книгой, парсим ее как книгу и вносим месяц и год прочтения в результат
            elif 'book-item-manage' in block['class']:
                book = ParserFromHTML.book(block, formatter)
                book['month'] = month
                book['year'] = year
                result.append(book)
        return result

    @staticmethod
    def book(bsoup: bs4.BeautifulSoup, formatter: BookDataFormatter = BookDataFormatter) -> Dict[str, str]:
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
        for property_name, parser_function in formatter.all_properties_parser().items():
            try:
                if hasattr(ParserFromHTML, parser_function):
                    result[property_name] = getattr(ParserFromHTML, parser_function)(bsoup)
            except AttributeError:
                logging.exception(f'No parser function {parser_function} is found!', exc_info=True)
        return result

    @staticmethod
    def get_author_name(bsoup: bs4.BeautifulSoup) -> str:
        result = bsoup.find('a', class_='brow-book-author')
        if result and bool(result.text):
            return ParserFromHTML._clear_name(result.text)
        else:
            return None

    @staticmethod
    def get_author_id(bsoup: bs4.BeautifulSoup) -> str:
        author_id = re.compile(r'(?<=/author/)\d+(?=-)')
        link = bsoup.find('a', class_='brow-book-author')
        if link:
            result = re.search(author_id, link.get('href'))
            return int(result.group()) if result else None
        else:
            return None

    @staticmethod
    def get_book_name(bsoup: bs4.BeautifulSoup) -> str:
        result = bsoup.find('a', class_='brow-book-name')
        if result and bool(result.text):
            return Parser._clear_name(result.text)
        else:
            return None

    @staticmethod
    def get_book_id(bsoup: bs4.BeautifulSoup) -> str:
        book_id = re.compile(r'(?<=/book/)\d+(?=-)')
        link = bsoup.find('a', class_='brow-book-name')
        if link:
            result = re.search(book_id, link.get('href'))
            return int(result.group()) if result else None
        else:
            return None

    @staticmethod
    def get_work_id(bsoup: bs4.BeautifulSoup) -> str:
        book_id = re.compile(r'(?<=/work/)\d+(?=-)')
        link = bsoup.find('a', class_='brow-book-name')
        if link:
            result = re.search(book_id, link.get('href'))
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
                if re.match(more, i.text) == None:
                    result.append(i.text)
        return ';'.join(result)

    @staticmethod
    def get_review_id(bsoup: bs4.BeautifulSoup) -> int:
        result = None
        review_id = re.compile(r'(?<=review-)\d+(?=-full)')
        div = bsoup.find(id=review_id)
        if div != None:
            result = int(re.search(review_id, div['id']).group())
        return result

    @staticmethod
    def get_review_text(bsoup: bs4.BeautifulSoup) -> str:
        result = None
        review_id = re.compile(r'(?<=review-)\d+(?=-full)')
        div = bsoup.find(id=review_id)
        if div != None:
            # сохраняем текст рецензии
            body = ''.join([str(p) for p in div.find('div', itemprop='reviewBody').contents])
            # ищем и сохраняем
            events = div.find('div', class_='event-pad')
            extra = ''.join([str(p) for p in events.contents]) if events != None else ''
            result = body + extra
        return result

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
                last_number = int(re.search(r'(?<=~)\d+', last_page['href']).group())
                result = [i for i in range(1, last_number + 1)]
            # если все страницы умещаются в низу страницы (их мало, до пяти штук)
            else:
                result = [int(i) for i in paginator.text.split()]
            return result


class ParserForDB(Parser):
    @staticmethod
    def prepare_book_for_db(book: Dict, formatter=BookDataFormatter) -> List:
        """
        Преобразует книгу для сохранения в БД в соответствии с BookDataFormatter.
        Нужен в случае, если название колонки в БД отличается от названия свойства парсера или
        требуется предварительная обработка значения свойства.
        :param book: словарь с информацией про книгу вида {'parser_field_name1':'field_value1','parser_field_name2':'field_value2'}
        :type book: Dict
        :param formatter: класс форматтера
        :type formatter: Class
        :return: словарь для сохранения  в БД вида {'db_field_name1':'field_value1', 'db_field_name2':'field_value2', ... }
        :rtype: Dict
        """
        new_book = {}
        for property in formatter.all_properties_db().keys():
            value = book.get(property, None)
            if value == None: value = ''
            new_book[formatter.common[property]['db']['name']] = value
        return new_book

    @staticmethod
    def prepare_books_for_db(books: List[Dict], formatter=BookDataFormatter) -> List:
        """
        Преобразует список книг для сохранения в БД в соответствии с BookDataFormatter.
        Нужен в случае, если название колонки в БД отличается от названия свойства парсера или
        требуется предварительная обработка значения свойства.
        :param books: список книг вида [{'parser_field_name1':'field_value1','parser_field_name2':'field_value2'},{}]
        :type books: List[Dict]
        :param formatter: класс форматтера
        :type formatter: Class
        :return: список для сохранения  в БД вида [{'db_field_name1':'field_value1', 'db_field_name2':'field_value2'}, {}]
        :rtype: List[Dict]
        """
        result = []
        for book in books:
            result.append(ParserForDB.prepare_book_for_db(book, formatter=formatter))
        return result


class ParserForCSV(Parser):
    @staticmethod
    def create_filepath_csv(login: str) -> str:
        """
        Возвращает путь и безопасное имя файла CSV формата 'login-YYYY-MM-DD--HH-MM-SS.csv'.
        Из логина читателя будут удалены небезопасные символы.
        :param login: логин читателя
        :type login: str
        :return:
        :rtype: str
        """
        login = login.translate(str.maketrans('', '', '\/:*?"<>|'))
        filename = login + "-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + '.csv'
        # @todo тут должна задаваться папка для сохранения csv
        return (os.path.join('csv', filename))

class ParserForXLSX(Parser):
    @staticmethod
    def prepare_book_for_xlsx(book: Dict, formatter=BookDataFormatter) -> List:
        """
        Преобразует книгу для сохранения в XLSX в соответствии с BookDataFormatter.
        Нужен в случае, если название колонки в XLSX отличается от названия свойства парсера или
        требуется предварительная обработка значения свойства.
        :param book: словарь с информацией про книгу вида {'parser_field_name1':'field_value1','parser_field_name2':'field_value2'}
        :type book: Dict
        :param formatter: класс форматтера
        :type formatter: Class
        :return: словарь для сохранения  в XLSX вида {'db_field_name1':'field_value1', 'db_field_name2':'field_value2', ... }
        :rtype: Dict
        """
        new_book = {}
        for property in formatter.all_properties_xlsx().keys():
            method = formatter.all_properties_xlsx()[property].get('method', None)
            value = book.get(property, None)
            if value == None:
                value = ''
            elif method and hasattr(ParserForXLSX, method):
                value = getattr(ParserForXLSX,method)(value)
            new_book[property] = value
        return new_book