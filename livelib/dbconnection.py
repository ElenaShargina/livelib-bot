import logging
import sqlite3
import os
from .parser import BookDataFormatter
from typing import Dict, List

class DBConnection:
    pass

class SQLite3Connection(DBConnection):
    folder = 'db'

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
            cursor = con.cursor()
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
                con.commit()
            except sqlite3.Error:
                logging.exception('Error while processing sql!', exc_info=True)
                raise
            cursor.close()
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
        :param fields_dict: список вида ({'name': 'name_value', 'type': type_value}, {}, ...)
        :type fields_dict:
        """
        fields_str = ','.join(["id INTEGER NOT NULL PRIMARY KEY"] + [i['name']+' '+i['type'] for i in fields_dict])
        sql = f"CREATE TABLE {name} ({fields_str})"
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {name}!", exc_info=True)
            raise

    def insert_values(self, values:List[Dict]):
        pass




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

