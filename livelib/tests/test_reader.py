import os, sys

# скрипт для правильной отработки тестов в github.actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from livelib import *
import logging

from utils import get_correct_filename, CustomUnitTest


class TestReader(CustomUnitTest):
    # папка с данными для проведения тестов
    # внутри её есть подпапки для конкретных функций
    test_folder: str = 'data/sample/test_reader'
    # файл с конфигом для проведения тестов.
    # тесты имеют собственную папку кеша веб-страниц
    config_file: str = '.env.reader'

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = Config(get_correct_filename(cls.config_file, ''))
        cls.connection = WebWithCache(cls.config)
        logging.basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                            format="%(asctime)s %(levelname)s %(message)s")
        cls.parser = ParserFromHTML

    def test_exists(self):
        pass



