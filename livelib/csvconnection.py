import csv
import logging

class CSVConnection:
    @staticmethod
    def create_file(filename, col_names, values):
        try:
            with open(filename, mode='w') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(col_names)
                writer.writerows(values)
        except Exception:
            logging.exception(f'Can not open or file {filename}. ', exc_info=True)
