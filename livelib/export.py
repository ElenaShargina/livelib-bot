import csv
import logging
import datetime

import datetime as datetime
import os.path
import string

import openpyxl
from openpyxl import Workbook
from .parser import BookDataFormatter, ParserForXLSX
from .config import Config

class Export:
    pass

# другой способ, тесно связанный с Экселем. https://www.excelguide.ru/2019/12/excel-python-basics.html
# @todo для csv убрать из рецензий теги, сделать ли ссылки? возможный экспорт в bookmate?
class CSVExport(Export):
    @staticmethod
    def create_file(filename, col_names, values, config:Config):
        try:
            # @todo КОДировку брать из настроек
            with open(filename, mode='w', newline='', encoding=config.encoding) as f:
                writer = csv.DictWriter(f, fieldnames=col_names, dialect='excel')
                writer.writeheader()
                writer.writerows([{i:j for i,j in row.items() if i in col_names} for row in values])
        except Exception:
            logging.exception(f'Can not open or file {filename}. ', exc_info=True)

class XLSXExport(Export):
    def __init__(self, config: Config):
        self.folder = config.export.xlsx.folder
        self.encoding = config.encoding

    def create_filename(self, reader_name: str) -> str:
        """
        Возвращает имя файла экспорта для читателя с добавленной датой экспорта. Считаем, что имя читателя берется из
        его логина в БД, поэтому безопасно для использования в имени файла.
        """
        if reader_name == '' or None:
            logging.exception('При экспорте не был указан логин читателя!')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')
        filename =  timestamp+'-'+reader_name+'.xlsx'
        return os.path.join(self.folder, filename)

    def create_file(self, books: list, login: str) -> str or None:
        """
        Сохраняет файл с заданными книгами в формате xlsx для читателя с заданным логином.
        Логин будет использован в названии файла.
        :type books: list
        :type login: str
        :return: путь к сохраненному файлу
        :rtype str:
        """
        properties = BookDataFormatter.all_properties_xlsx()
        print(properties)

        filename = self.create_filename(login)
        print(filename)

        wb = Workbook()
        ws = wb.active
        ws.title = 'Прочитанные книги'

        # Задаем ширину столбцов. Она берется из BookDataFormatter
        index = string.ascii_uppercase
        i = 0
        for value in properties.values():
            if value.get('column_width', None) and i<26:
                ws.column_dimensions[index[i]].width = value['column_width']
                i+=1

        # Задаем названия столбцов
        title_row = [i['name'] for i in properties.values()]
        print(title_row)
        ws.append(title_row)

        # Вводим данные про все книги
        for book in books:
            prepared_book = ParserForXLSX.prepare_book_for_xlsx(book)
            ws.append(list(prepared_book.values()))

        try:
            wb.save(filename)
            logging.info(f'Successfully saved! Export file with {len(books)} books in xlsx for reader {login} at {filename}')
        except Exception as exc:
            logging.exception(f'Не удалось сохранить файл c экспортом по адресу {filename}')
            return None

        # wb = openpyxl.load_workbook(filename, read_only=False)
        # ws = wb.worksheets[0]
        # print(ws)
        # i = 1
        # for name,value in properties.items():
        #     if value.get('column_width', None):
        #         ws.column_dimensions[name].width = value['column_width']
        #     i+=1
        # print(ws.column_dimensions)
        # wb.save(filename)



