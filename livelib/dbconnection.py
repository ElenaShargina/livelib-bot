import logging
import sqlite3
import os

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
            logging.error(f'Error while connecting to {self.filename} db.', exc_info=True)
        else:
            con.close()

    def run_sql(self, sql: str) -> int or None:
        result = None
        try:
            con = sqlite3.connect(self.filename)
            cursor = con.cursor()
            try:
                cursor.execute(sql)
                result = cursor.rowcount
                con.commit()
            except sqlite3.Error as error:
                print('Error with sqlite!', error)
            cursor.close()
            con.close()
        except sqlite3.Error as error:
            logging.error(f'Error while processing sql {sql} in {self.filename} SQLiteConnection! ', error)
        return result


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

