import re
from bs4 import BeautifulSoup as bs
from connection import *


class Reader:
    def __init__(self, login, connection:Connection):
        self.login = login
        self.connection = connection

    @property
    def prefix(self):
        return 'reader/'+self.login

    # @TODO вставить тесты на неправильный ответ, на отcутствие читателя
    def get_main_page(self):
        page = self.connection.get_page(self.prefix)
        if page != None:
            bs_page = bs(page, self.connection.bs_parser)
            return bs_page
        else:
            return None

    def get_books_from_page(self, url):
        page = self.connection.get_page(url)
        if page != None:
            bs_page = bs(page, self.connection.bs_parser)
            all_books = bs_page.find_all('div', attrs={'class':'book-item-manage'})
            print(all_books)
            res = [book.find('a', attrs={'class':'brow-book-name'}).text for book in all_books]
            return res

    def get_all_books(self):
        page = self.connection.get_page(self.prefix + 'read/listview/smalllist')
        # @todo рассмотреть другие случаи
        if page != None:
            bs_page = bs(page, self.connection.bs_parser)
            last_page_url = bs_page.find('div', attrs={'id':'booklist-pagination'}).find('span', attrs={'class':'i-pager-last'}).find_parent('a')['href']
            # @todo проверить правильность регулярного выражения
            last_page = re.search(r'\d+$',last_page_url).group()
            print(last_page)
            book_list_pages = []
            for i in range(int(last_page)):
                book_list_pages.append(f'{self.prefix}/read/listview/smalllist/~{i}')

            for url in book_list_pages:
                print(url)
                print(self.get_books_from_page(url))

