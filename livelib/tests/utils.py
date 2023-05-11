import os
import unittest
from livelib import Config, Parser, WebConnection
import json
import bs4
from bs4 import BeautifulSoup as bs

def get_correct_filename(filename: str, folder: str, ) -> str:
    """
    служебная функция для получения корректного пути до тестовых файлов конфига, дб и тд,
    нужна для правильной отработки тестов в Github Actions
    """
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    prefix_folder = os.path.join(parent_dir, *folder.split('/'))
    return os.path.join(prefix_folder, filename)

class CustomUnitTest(unittest.TestCase):

    config: Config
    parser: Parser
    test_folder: str
    connection : WebConnection

    def _str_to_bs(self, x: str) -> bs:
        """
        Служебная функция, переформартирует строку в объект BeautifulSoup
        в соответствии с настройками имеющегося экземпляра WebConnection
        """
        return bs(x, self.connection.bs_parser)

    def process_json_compare_to_json(self, method: str, folder: str, json_output_name: str,  json_input_name :str = 'html',
                                     convert_html_to_bs: bool = True) -> None:
        """
        Тестируем метод на небольшой вводной информации (как правило - небольших кусках html),
        для удобства вынесенных в отдельный файл file.json вместе с ожидаемыми результатами.
        Структура json файла:
        [{'<json_input_name>':'вводная информация', '<json_output_name>':'правильный ответ метода'}, {}, ...]
        Общая структура папок: <cls.test_folder>/
                                                <folder>/
                                                        file.json

        :param method: название метода, который будем тестировать
        :type method: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        :param json_output_name: название свойства в json-файле с правильным ответом
        :type json_output_name: str
        :param json_input_name: название свойства в json-файле с входящей информацией
            defaults to 'html'
        :type json_input_name: str
        :param convert_html_to_bs: конвертировать ли html из <json_input_name> в объект BeautifulSoup
            defaults to True
        :type convert_html_to_bs: bool
        """
        filename = get_correct_filename('file.json', os.path.join(self.test_folder, folder))
        with open(filename, mode='r', encoding=self.config.encoding) as f:
            cases = json.load(f)
            for i in cases:
                with self.subTest(f'Test with {i[json_output_name]}'):
                    input = self._str_to_bs(i[json_input_name]) if convert_html_to_bs else i[json_input_name]
                    self.assertEqual(i[json_output_name], getattr(self.parser, method)(input))

    def process_html_compare_to_json(self, method: str, folder: str, convert_html_to_bs: bool = True) -> None:
        """
       Тестируем метод на большой вводной информации (как правило - целых страницах html),
       для удобства вынесенных в отдельные файлы.
       Общая структура папок: <cls.test_folder>/
                                               N/
                                                file.html
                                                correct_output.json
        где N - произвольные названия подпапок (метод просканирует папку <cls.test_folder> полностью).

       :param method: название метода, который будем тестировать
       :type method: str
       :param folder: папка, где хранятся тестовые данные
       :type folder: str
       :param json_output_name: название свойства в json-файле с правильным ответом
       :type json_output_name: str
       :param convert_html_to_bs: конвертировать ли html из html файла в объект BeautifulSoup
           defaults to True
       :type convert_html_to_bs: bool
       """

        """
        Тестируем на БОЛЬШИХ кусках html, для удобства вынесенных в ОТДЕЛЬНЫЙ файл file.html
        Результат парсинга сравниваем с заранее сохраненными образцами в correct_output.json файлах.
        Общая структура папок: /<folder>/1/file.html, correct_output.json
        :param method: название метода ParserFromHTML, который будем тестировать
        :type method: str
        :param folder: папка, где хранятся тестовые данные
        :type folder: str
        :param convert_html_to_bs: конвертировать ли html в BeautifulSoup
            defaults to True
        :type convert_html_to_bs: bool
        """
        prefix_folder = os.path.join(get_correct_filename('', self.test_folder), folder)
        # просматриваем, какие папки с тестовыми данными есть в <folder>
        # в каждой папке должен быть file.html с html кодом и dump.json, где сохранен правильный ответ парсинга
        with os.scandir(prefix_folder) as files:
            subdirs = [file.name for file in files if file.is_dir()]
        # для каждой папки сличаем результат парсинга и правильный сохраненный ответ
        for i in subdirs:
            with open(os.path.join(prefix_folder, str(i), 'file.html'), mode='r',
                      encoding=self.connection.encoding) as f1:
                input = self._str_to_bs(f1.read()) if convert_html_to_bs else f1.read()
                output = getattr(self.parser, method)(input)
                # print(output)
                f1.close()
            # код для обновления файлов с правильными ответами
            # with open(os.path.join(prefix_folder, str(i), 'correct_output.json'), mode='w', encoding=self.connection.encoding) as f3:
            #     json.dump(output,f3, indent=4, ensure_ascii=False)
            #     f3.close()
            with open(os.path.join(prefix_folder, str(i), 'correct_output.json'), mode='r',
                      encoding=self.connection.encoding) as f2:
                correct_output = json.load(f2)
                f2.close()
            with self.subTest(f'Test method {method} with {i} subdir.'):
                self.assertEqual(output, correct_output)