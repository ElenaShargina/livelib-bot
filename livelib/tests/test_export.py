import datetime
import json
import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_correct_filename, CustomUnitTest, remove_file
import unittest
import logging
from livelib import *

class TestXLSXExport(CustomUnitTest):
    # папка с данными для проведения тестов
    # внутри её есть подпапки для конкретных функций
    test_folder: str = 'data/sample/test_export/xlsx'
    # файл с конфигом для проведения тестов.
    # тесты имеют собственную папку кеша веб-страниц
    config_file: str = '.env.export'

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.web_connection = WebWithCache(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML

    def test_create_filename(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')
        values = [{'reader_name':'some_reader', 'folder':'xlsx', 'output':f"xlsx\\{timestamp}-some_reader.xlsx"},
                  {'reader_name':'Foo', 'folder':'xlsx\somefolder', 'output':f"xlsx\\somefolder\\{timestamp}-Foo.xlsx"},
                  {'reader_name':'some_reader', 'folder':'', 'output':f"{timestamp}-some_reader.xlsx"}]
        for i in values:
            special_config = Config(get_correct_filename(self.config_file, ''))
            special_config.export.xlsx.folder = i['folder']
            export = XLSXExport(special_config)
            self.assertEqual(i['output'], export.create_filename(i['reader_name']))

    def test_create_file(self):
        pass
