from livelib import BookDataFormatter, Reader, Config, WebWithCache, SQLite3Connection, XLSXExport

config = Config('.env')
web = WebWithCache(config)
db = SQLite3Connection(config.db_config.sqlite_db)
formatter = BookDataFormatter
xlsx = XLSXExport(config)

r = Reader('Feana', web, db, xlsx)
r.register()
# books = r.get_read_books_from_web()
# r.save_read_books_in_db(books)
books = r.get_read_books_from_db()
print(r.create_export_xlsx_file())

