from livelib import *

config = Config('.env')
db = SQLite3Connection(config.db_config.sqlite_db)
db.create_db(BookDataFormatter)
# web = WebWithCache(config, random_sleep=True)
web = SimpleWeb(config,random_sleep=False)

current_reader = Reader(login='', web_connection=web, db_connection=db, parser_html=ParserFromHTML, parser_db=ParserForDB)

# Есть ли пользователь на ЛЛ
login = input('Ввести логин \n')

if current_reader.exists(login=login):
    # # # если есть логин на ЛЛ
    print('Вы существуете!')
    # есть ли пользователь в БД?
    last_update = current_reader.has_db_entries()
    if last_update:
        # # если есть пользователь
        print(f'У вас есть записи от {last_update}!')
        # # # Скачать новые записи?
        update = input('Скачать новые записи?')
        if update == '1':
        # # # # Если скачать
            pass
        else:
        # # # # Если не надо скачивать
            pass
    else:
    # # если нет пользователя в БД
        print('У вас нет записей, начинаем скачивание...')
else:
    # # # если нет логина на ЛЛ
    print('Вы не существуете!')



