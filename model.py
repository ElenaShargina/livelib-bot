from livelib import *

config = Config('.env')
db = SQLite3Connection(config.db_config.sqlite_db, create_if_not_exist=True)
db.create_db(BookDataFormatter)
# @todo почему не ругается?
# web = WebWithCache(config, random_sleep=True)
web = WebWithCache(config,random_sleep=False)

current_reader = Reader(login='', web_connection=web, db_connection=db, parser_html=ParserFromHTML, parser_db=ParserForDB)

# Есть ли пользователь на ЛЛ
# login = input('Ввести логин \n')
login = 'Inelgerdis'
if current_reader.exists(login=login):
    # # # если есть логин на ЛЛ
    print('Вы существуете!')
    # есть ли пользователь в БД?
    last_update = current_reader.has_db_entries()
    if last_update:
        # # если есть пользователь
        print(f'У вас есть записи от {last_update}!')
        # # # Скачать новые записи?
        update = input('Скачать записи заново?')
        if update == '1':
        # # # # Если скачать
            current_reader.update_books()
            pass
        else:
        # # # # Если не надо скачивать
            pass
    else:
    # # если нет пользователя в БД
        print('У вас нет записей, начинаем скачивание...')
        current_reader.register()
        print('currrrent_id=', current_reader.id)
        current_reader.get_all_read_books()
    # reader.create_export_file(type='csv')
else:
    # # # если нет логина на ЛЛ
    print('Вы не существуете!')



