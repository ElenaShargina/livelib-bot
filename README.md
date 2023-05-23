# Экспорт данных с сайта livelib.ru
<p>У популярного сайта для учета прочитанных книг livelib.ru нет собственной функции экспорта
или открытого API для экспорта данных. Проект решает эту проблему, позволяя получить свои прочитанные книги в файле формата xlsx.</p>
<b>Проблемы:</b>
<ul><li>сайт livelib.ru не обладает открытым API, поэтому нужен парсинг html-страниц;</li>
<li>сайт livelib.ru ставит защиту от частых запросов (капча или просто сброс), поэтому генерировать запросы приходится с задержкой;</li>
<li>для частичного решения этой проблемы запрошенные книги сохраняются в базе данных и предоставляется возможность скачать их оттуда без новых запросов к сайту.</li>
</ul>


## Версия 1.0
 - проверяет, существует ли читатель с заданным логином
 - загружает прочитанные читателем книги в локальной БД
 - экспортирует прочитанные читателем книги в xlsx формате

## Использование
<p>Пример использования пакета приведен в model.py.</p>
<p align='center'><img src='http://feana.ru/wp-content/uploads/2023/05/user_case_v1.png' alt='User case v1'/></p>

## Структура проекта:
- /cache/ папка для хранения кеша страниц
- /db/ - папка для хранения БД
- /export/ - папка для хранения созданных файлов с экспортированными данными
- /livelib/ - пакет livelib
        tests/ - папка с юнит-тестами пакета, в ней содержатся необходимые тестовые данные (файлы, базы данных)
- /uml-diagrams/ - папка с некоторыми uml-диаграммами, относящимися к проекту
- log.log - файл лога
- model.py - демонстрация работы пакета
- README.txt - текущий файл
- requirements.txt - файл с версиями необходимых пакетов Python

- .github/workflows - для ГитХаба прописано автоматическое тестирование пакета с помощью unit tests при каждом пуше.

## Структура классов
<p align='center'><img src='http://feana.ru/wp-content/uploads/2023/05/Classes.png' alt='Структура классов пакета' height='400px'/></p>

## Схема базы данных
<p align='center'><img src='http://feana.ru/wp-content/uploads/2023/05/Database.png' alt='Схема базы данных'/></p>

## Требования
Требуемые пакеты перечислены в requirements.txt

## Тестирование
Проект покрыт юнит-тестами из папки livelib/tests. При пуше на github они запускаются автоматически.

## Пример работы основной функции по парсингу и экспорту всех прочитанных книг
<p align='center'><img src='http://feana.ru/wp-content/uploads/2023/05/reader_get_all_read_books-1.png' alt='Диаграмма последовательности работы метода' height='400px'/></p>

## В следующих версиях
- добавить экспорт в csv формат
- добавить прикрепление ISBN (требует парсинга дополнительных страниц сайта)
- добавить экспорт в формате, подходящим для импорта на BookMate
- добавить экспорт книг из виш-листа
- расширение сценариев использования:
<p align='center'><img src='http://feana.ru/wp-content/uploads/2023/05/user_case_v2_v3.png' alt='User case v2, v3' height='400px' /></p>
