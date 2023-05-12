import json
import logging
import sqlite3
import os
from livelib.parser import BookDataFormatter
from typing import Dict, List
from livelib.config import Config

class DBConnection:
    pass

class SQLite3Connection(DBConnection):
    table_book = 'Book'
    table_reader = 'Reader'
    table_readbook = 'ReadBook'

    def __init__(self, filename: str, create_if_not_exist:bool=False):
        self.filename = filename
        # создаем файл с базой данной, если требуется
        if not os.path.isfile(self.filename):
            try:
                f = open(self.filename, mode='w')
                f.close()
                logging.info(f'Create DB file {self.filename}')
            except Exception as exc:
                logging.exception(f'Can not create DB file {self.filename}', exc_info=True)
        try:
            con = sqlite3.connect(self.filename)
            logging.info(f'Successfully connected to {self.filename} db.')
        except sqlite3.Error:
            logging.exception(f'Error while connecting to {self.filename} db.', exc_info=True)
            raise
        else:
            con.close()

    def create_db(self, formatter: type[BookDataFormatter] = BookDataFormatter) -> None:
        """
        Создание базы данных по заданным в BookDataFormatter полям.
        Создает три таблицы: Book, Reader, ReadBook. Подробнее в прилагаемой к проекту диаграмме.
        """
        logging.debug('Starting to create new database.')
        # создаем таблицу книг
        book_fields: dict[str,str] = {i:formatter.all_properties_db()[i] for i in formatter.book_properties_db}
        fields_str = ','.join(["id INTEGER PRIMARY KEY AUTOINCREMENT "] + [i+' '+j for i,j in book_fields.items()])
        sql = f"CREATE TABLE {self.table_book} ( {fields_str})"
        logging.debug(f'Creating new table: {sql}')
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {self.table_book}!", exc_info=True)
            raise
        # создаем таблицу читателей
        reader_fields: dict[str,str] = {i:formatter.all_properties_db()[i] for i in formatter.reader_properties_db}
        fields_str = ','.join(["id INTEGER PRIMARY KEY AUTOINCREMENT "] + [i+' '+j for i,j in reader_fields.items()])
        sql = f"CREATE TABLE {self.table_reader} ( {fields_str})"
        logging.debug(f'Creating new table: {sql}')
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {self.table_reader}!", exc_info=True)
            raise
        # создаем таблицу прочитанных книг
        readbook_fields: dict[str,str] = {i:formatter.all_properties_db()[i] for i in formatter.readbook_properties_db}
        fields_str = ','.join(["id INTEGER PRIMARY KEY AUTOINCREMENT "] +
                              ["book_id INTEGER "] +
                              ["reader_id INTEGER "] +
                              [i+' '+j for i,j in readbook_fields.items()] +
                              [f"FOREIGN KEY(book_id) REFERENCES {self.table_book}(id) "] +
                              [f"FOREIGN KEY(reader_id) REFERENCES {self.table_reader}(id) "]
                              )
        sql = f"CREATE TABLE {self.table_readbook} ( {fields_str})"
        logging.debug(f'Creating new table: {sql}')
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {self.table_readbook}!", exc_info=True)
            raise


    def run_single_sql(self, sql: str) -> int or None:
        result = None
        try:
            con = sqlite3.connect(self.filename)
            try:
                with con:
                    result = con.execute(sql).fetchall()
            except sqlite3.Error:
                logging.exception('Error while processing sql!', exc_info=True)
                raise
            con.close()
        except sqlite3.Error:
            logging.exception(f'Error while processing sql {sql} in {self.filename} SQLiteConnection! ', exc_info=True)
            raise
        return result

    def insert_values(self, table: str, values: List[Dict]) -> int:
        """
        Вставляет несколько новых строк в БД. Должно быть согласовано с DataFormatter
        :param table: название базы данных
        :type table: str
        :param values: список вида [{'field_name1':'field_value1','field_name2':'field_value2',...},{...}], где каждый словарь это новая строка
        :type values: list[Dict]
        :return: количество вставленных строк
        :rtype: int
        """
        result = 0
        field_names = ', '.join([i for i in values[0].keys()])
        field_values = [[val for val in book.values()] for book in values]
        placeholders = ', '.join(['?' for i in range(len(values[0].keys()))])
        # print('field_names:', field_names)
        # print('field_values:', field_values)
        # print('placeholders:', placeholders)
        try:
            con = sqlite3.connect(self.filename)
            try:
                with con:
                    result = con.executemany(f"INSERT INTO {table} ({field_names}) VALUES ({placeholders})", field_values).rowcount
            except sqlite3.Error:
                logging.exception('Error while processing sql!', exc_info=True)
                raise
            con.close()
        except sqlite3.Error:
            logging.exception(f'Error while processing executemany in {self.filename} SQLiteConnection! ', exc_info=True)
            raise
        return result

    def table_exists(self, name:str) -> bool:
        """
        Проверяет, существует ли таблица с заданным именем.
        :param name: название таблицы
        :type name: str
        :return: True, если существует, иначе False
        :rtype: bool
        """
        result = False
        try:
            con = sqlite3.connect(self.filename)
            try:
                with con:
                    result = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
                    result = True if result!=None else False
            except sqlite3.Error:
                logging.exception('Error while processing sql!', exc_info=True)
                raise
            con.close()
        except sqlite3.Error:
            logging.exception(f'Error while connecting to database in {self.filename} SQLiteConnection! ', exc_info=True)
            raise
        finally:
            return result

    def get_table_schema(self, table: str) -> str:
        """
        Возвращает схему таблицы в виде сериализованной для json строки
        :param table: название таблицы
        :type table: str
        :return:
        :rtype: str
        """
        if self.table_exists(table):
            result =  self.run_single_sql(f'PRAGMA table_info({table})')
            return json.dumps(result)
        else:
            return None


