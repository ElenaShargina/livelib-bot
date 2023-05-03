from bs4 import BeautifulSoup as bs

class BSParser:
    @staticmethod
    def reader_prefix(login):
        return '/reader/'+login

    @staticmethod
    def reader_all_books(login):
        return BSParser.reader_prefix(login) + '/read/listview/smalllist'

    @staticmethod
    def check_404(text):
        if text.find('title', string='404 @ LiveLib'):
            return True
        else:
            return False

    @staticmethod
    def all_books_from_page(bsoup):
        return bsoup.find_all('div', attrs={'class':'book-item-manage'})
