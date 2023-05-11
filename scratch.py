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
    db = SQLite3Connection(f'db/{login}.db')
    formatter = BookDataFormatter
    r = Reader(login, WebWithCache(config, random_sleep=True), db)
    db.create_table(r.login, BookDataFormatter.all_properties_db())

    books = r.get_all_read_books()

    CSVConnection.create_file(r.parser.create_filepath_csv(r.login), BookDataFormatter.all_properties_csv().keys(), books, config)

for i in ['Eugenia_Novik', 'Feana', 'Kasssiopei', 'ElviraYakovleva', 'Shakespeare']:
    get_all(i)
