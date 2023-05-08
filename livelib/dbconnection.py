import logging
import sqlite3
import os
from livelib.parser import BookDataFormatter
from typing import Dict, List
from livelib.config import Config

class DBConnection:
    pass

class SQLite3Connection(DBConnection):
    def __init__(self, filename: str):
        self.filename = filename
        try:
            con = sqlite3.connect(self.filename)
            logging.info(f'Successfully connected to {self.filename} db.')
        except sqlite3.Error:
            logging.exception(f'Error while connecting to {self.filename} db.', exc_info=True)
            raise
        else:
            con.close()

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

    def create_table(self, name:str, fields_dict: List[Dict]):
        """
        Создает таблицу с заданным названием и структурой
        :param name:
        :type name:
        :param fields_dict: словарь вида {'name_field1':'type_field1', 'name_field2':'type_field2', ...}
        :type fields_dict:
        """
        fields_str = ','.join(["id INTEGER PRIMARY KEY AUTOINCREMENT "] + [i+' '+j for i,j in fields_dict.items()])
        #@todo небезопасно вот тут
        sql = f"CREATE TABLE {name} ({fields_str})"
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {name}!", exc_info=True)
            raise

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

    def get_table_schema(self, table:str) -> list[tuple]:
        if self.table_exists(table):
            return self.run_single_sql(f'PRAGMA table_info({table})')
        else:
            return None

    # def create_tables(self):
    #     con = sqlite3.connect(self.filename)
    #     cursor = con.cursor()
    #     sql = """CREATE TABLE Books(id INTEGER NOT NULL PRIMARY KEY,
    #           title TEXT,
    #           author TEXT)"""
    #     cursor.execute(sql)
    #     con.commit()
    #     cursor.close()
    #     con.close()

