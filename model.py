from livelib import *

config = Config('.env')
db = SQLite3Connection(config.db_config.sqlite_db)
# web = WebWithCache(config, random_sleep=True)
web = SimpleWeb(config,random_sleep=False)

current_reader = Reader(login='', web_connection=web, db_connection=db, parser_html=ParserFromHTML, parser_db=ParserForDB)

login = input('Ввести логин \n')

# Есть ли пользователь на ЛЛ
if current_reader.exists(login=login):
    print('Вы существуете!')

    if current_reader.has_db_entries():
        print('У вас есть записи!')
    else:
        print('У вас нет записей, начинаем скачивание...')

else:
    print('Вы не существуете!')


# есть ли пользователь в БД?

# # если есть пользователь

# # # Скачать новые записи?

# # # # Если скачать

# # # # Если не надо скачивать

# # если нет пользователя

# # # если есть логин на ЛЛ

# # # если нет логина на ЛЛ



