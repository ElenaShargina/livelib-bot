import csv
import logging
from .config import Config

# другой способ, тесно связанный с Экселем. https://www.excelguide.ru/2019/12/excel-python-basics.html
# @todo для csv убрать из рецензий теги, сделать ли ссылки? возможный экспорт в bookmate?
class CSVConnection:
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
