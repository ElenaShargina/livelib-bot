import json
import logging
import sqlite3
import os
import typing

from livelib.parser import BookDataFormatter
from livelib.config import Config
from typing import Dict, List


class DBConnection:
    """
    Абстрактный класс соединения с БД.
    """

    def create_db(self, formatter: type[BookDataFormatter] = BookDataFormatter) -> None:
        """
        Создание базы данных по заданным в BookDataFormatter полям.
        :param formatter: класс BookDataFormatter со словарем данных по каждому столбцу БД
                            вида {'название_поля1':'тип_поля1', 'название_поля2':'тип_поля1', ...}
                defaults to BookDataFormatter
        :type formatter: type[BookDataFormatter]
        """
        pass

    def run_single_sql(self, sql: str, params: typing.Iterable = (), return_lastrowid=False) -> list or int or None:
        """
        Запускает одну команду sql, переданную в строке sql с подставленными параметрами params.
        Невозможно с помощью подстановки параметров создать таблицу, удалить таблицу, проверить схему таблицы,
        поэтому в таких случаях надо заранее собирать sql строку, обращая внимания на возможные sql инъекции.
        :param sql: запрос SQL с возможными placeholders (?) для параметров из params
        :type sql: str
        :param params: список, кортеж, словарь подставляемых параметров
        :type params: typing.Iterable
        :param return_lastrowid: Нужно ли возвращать ID последней добавленной строки
        :type return_lastrowid: Bool
                defaults to False
        :return: результат запроса или None
        :rtype: list|int|None
        """
        pass

    def insert_values(self, table: str, values: List[Dict]) -> int:
        """
        Вставляет несколько новых строк в БД. Должно быть согласовано с DataFormatter
        :param table: название базы данных
        :type table: str
        :param values: список вида [{'field_name1':'field_value1','field_name2':'field_value2',...},{...}],
                        где каждый словарь это новая строка
        :type values: list[Dict]
        :return: количество вставленных строк
        :rtype: int
        """
        pass

    def table_exists(self, name: str) -> bool:
        """
        Проверяет, существует ли таблица с заданным именем.
        :param name: название таблицы
        :type name: str
        :return: True, если существует, иначе False
        :rtype: bool
        """
        pass

    def get_table_schema(self, table: str) -> str or None:
        """
        Возвращает схему таблицы в виде сериализованной для json строки
        :param table: название таблицы
        :type table: str
        :return:
        :rtype: str
        """
        pass


class SQLite3Connection(DBConnection):
    """
    Класс работы с базой данных в формате sqlite3.
    Структура таблиц БД описана в uml_diagrams/Database.pdf

    ...
    Attributes
    ----------
    table_book : str
        Название таблицы с книгами
    table_reader : str
        Название таблицы с читателями
    table_readbook : str
        Название таблицы со связью Книга-Читатель

    Methods
    -------
    __init__(filename:str, create_if_not_exists:bool)
        Создает объект соединения с БД, создает файл БД, если нужно
    create_db(self, formatter: type[BookDataFormatter] = BookDataFormatter) -> None
        Создает базу данных по заданным в formatter полям
    run_single_sql(self, sql: str, params: typing.Iterable = (), return_lastrowid=False) -> list or None
        Запускает одну команду sql, переданную в строке sql с подставленными параметрами params
    insert_values(self, table: str, values: List[Dict]) -> int
        Вставляет несколько новых строк в БД.
    table_exists(self, name: str) -> bool
         Проверяет, существует ли таблица с заданным именем name.
    get_table_schema(self, table: str) -> str or None
        Возвращает схему таблицы в виде сериализованной для json строки
    """
    table_book: str = 'Book'
    table_reader: str = 'Reader'
    table_readbook: str = 'ReadBook'

    def __init__(self, config: Config, create_if_not_exist: bool = False):
        """
        Создает объект соединения с заданным файлом БД, создает этот файл, если указано
        :param filename: путь до файла БД
        :type filename: str
        :param create_if_not_exist: нужно ли создавать файл БД, если его не найдено
        :type create_if_not_exist: bool
        """
        self.filename: str = config.db.sqlite_db  # файл базы данных
        # создаем файл с базой данной, если требуется
        if not os.path.isfile(self.filename) and create_if_not_exist:
            try:
                f = open(self.filename, mode='w')
                self.create_db(BookDataFormatter)
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
        :param formatter: класс BookDataFormatter со словарем данных по каждому столбцу БД
                            вида {'название_поля1':'тип_поля1', 'название_поля2':'тип_поля1', ...}
                defaults to BookDataFormatter
        :type formatter: type[BookDataFormatter]
        """
        logging.debug('Starting to create new database.')
        # создаем таблицу книг
        book_fields: dict[str, str] = {i: formatter.all_properties_db()[i] for i in formatter.book_properties_db}
        fields_str = ','.join(["id INTEGER PRIMARY KEY AUTOINCREMENT "] + [i + ' ' + j for i, j in book_fields.items()])
        sql = f"CREATE TABLE {self.table_book} ( {fields_str} , UNIQUE(book_id), UNIQUE(work_id) )"
        logging.debug(f'Creating new table: {sql}')
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {self.table_book}!", exc_info=True)
            raise
        # создаем таблицу читателей
        reader_fields: dict[str, str] = {i: formatter.all_properties_db()[i] for i in formatter.reader_properties_db}
        fields_str = ','.join(
            ["id INTEGER PRIMARY KEY AUTOINCREMENT "] + [i + ' ' + j for i, j in reader_fields.items()])
        sql = f"CREATE TABLE {self.table_reader} ( {fields_str})"
        logging.debug(f'Creating new table: {sql}')
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {self.table_reader}!", exc_info=True)
            raise
        # создаем таблицу прочитанных книг
        readbook_fields: dict[str, str] = {i: formatter.all_properties_db()[i] for i in
                                           formatter.readbook_properties_db}
        fields_str = ','.join(["id INTEGER PRIMARY KEY AUTOINCREMENT "] +
                              ["book_id INTEGER "] +
                              ["reader_id INTEGER "] +
                              [i + ' ' + j for i, j in readbook_fields.items()] +
                              [
                                  f"CONSTRAINT fk_book_id FOREIGN KEY(book_id) REFERENCES {self.table_book}(id) ON DELETE CASCADE "] +
                              [
                                  f"CONSTRAINT fk_reader_id FOREIGN KEY(reader_id) REFERENCES {self.table_reader}(id) ON DELETE CASCADE "]
                              )
        sql = f"CREATE TABLE {self.table_readbook} ( {fields_str} UNIQUE(book_id, reader_id))"
        logging.debug(f'Creating new table: {sql}')
        try:
            self.run_single_sql(sql)
        except sqlite3.Error:
            logging.exception(f"Can't create table {self.table_readbook}!", exc_info=True)
            raise

    def run_single_sql(self, sql: str, params: typing.Iterable = (), return_lastrowid=False) -> list or int or None:
        """
        Запускает одну команду sql, переданную в строке sql с подставленными параметрами params.
        Невозможно с помощью подстановки параметров создать таблицу, удалить таблицу, проверить схему таблицы,
        поэтому в таких случаях надо заранее собирать sql строку, обращая внимания на возможные sql инъекции.
        :param sql: запрос SQL с возможными placeholders (?) для параметров из params
        :type sql: str
        :param params: список, кортеж, словарь подставляемых параметров
        :type params: typing.Iterable
        :param return_lastrowid: Нужно ли возвращать ID последней добавленной строки
        :type return_lastrowid: Bool
                defaults to False
        :return: результат запроса или None
        :rtype: list|int|None
        """

        def dict_factory(cursor, row):
            fields = [column[0] for column in cursor.description]
            return {key: value for key, value in zip(fields, row)}

        result = None
        try:
            con = sqlite3.connect(self.filename)
            con.row_factory = dict_factory
            cur = con.cursor()
            try:
                result = cur.execute(sql, params).fetchall()
                if return_lastrowid:
                    result = cur.lastrowid
                con.commit()
            except sqlite3.Error:
                logging.exception('Error while processing sql!', exc_info=True)
                # raise
            con.close()
        except sqlite3.Error:
            logging.exception(f'Error while processing sql {sql} in {self.filename} SQLiteConnection! ', exc_info=True)
            # raise
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
                    result = con.executemany(f"INSERT OR IGNORE INTO {table} ({field_names}) VALUES ({placeholders})",
                                             field_values).rowcount
            except sqlite3.Error:
                sep = "\n"
                logging.exception(f'Error while processing sql! table = {table}, \n'
                                  f'field_names = {field_names}, \n'
                                  f'place_holders = {placeholders}, \n'
                                  f'field_values = {sep.join([str(i) for i in field_values])}', exc_info=True)
                raise
            con.close()
        except sqlite3.Error:
            logging.exception(f'Error while processing executemany in {self.filename} SQLiteConnection! ',
                              exc_info=True)
            raise
        return result

    def table_exists(self, name: str) -> bool:
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
                    result = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                                         (name,)).fetchone()
                    result = True if result != None else False
            except sqlite3.Error:
                logging.exception('Error while processing sql!', exc_info=True)
                raise
            con.close()
        except sqlite3.Error:
            logging.exception(f'Error while connecting to database in {self.filename} SQLiteConnection! ',
                              exc_info=True)
            raise
        finally:
            return result

    def get_table_schema(self, table: str) -> str or None:
        """
        Возвращает схему таблицы в виде сериализованной для json строки
        :param table: название таблицы
        :type table: str
        :return:
        :rtype: str
        """
        if self.table_exists(table):
            result = self.run_single_sql(f'PRAGMA table_info ({table})')
            return json.dumps(result)
        else:
            return None
