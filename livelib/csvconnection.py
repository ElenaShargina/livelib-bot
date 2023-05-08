import csv
import logging

# другой способ, тесно связанный с Экселем. https://www.excelguide.ru/2019/12/excel-python-basics.html
# @todo для csv убрать из рецензий теги, сделать ли ссылки? возможный экспорт в bookmate?
class CSVConnection:
    @staticmethod
    def create_file(filename, col_names, values):
        try:
            # @todo КОДировку брать из настроек
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=col_names, dialect='excel')
                print(col_names)
                writer.writeheader()
                print(values)
                writer.writerows(values)
        except Exception:
            logging.exception(f'Can not open or file {filename}. ', exc_info=True)
