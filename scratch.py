import livelib.config
from livelib import *

from livelib.parser import BookDataFormatter

# Eugenia_Novik
# Feana
# Kasssiopei - 60 read books
# ElviraYakovleva - 13 read books
# Shakespeare - 2096 read books

def get_all(login):
    config = Config('.env')
    db = SQLite3Connection(config.db_config.sqlite_db)
    formatter = BookDataFormatter
    r = Reader(login, WebWithCache(config, random_sleep=True), db)
    # db.create_table(r.login, BookDataFormatter.all_properties_db())

    books = r.get_all_read_books()
    print(books)

    # import json
    # try:
    #     f3 = open('correct_output.json', mode='w', encoding='utf-8')
    #     json.dump(books, f3, indent=4, ensure_ascii=False)
    #     f3.close()
    # except Exception as exc:
    #     print(f'Error {exc}')


    # CSVConnection.create_file(ParserForCSV.create_filepath_csv(r.login), BookDataFormatter.all_properties_csv().keys(), books, config)

# for i in ['Eugenia_Novik', 'Feana', 'Kasssiopei', 'ElviraYakovleva', 'Shakespeare']:
for i in ['ElviraYakovleva', 'Feana']:
    get_all(i)



