from livelib import *

config = Config('.env')
db = SQLite3Connection(config.db_config.sqlite_db, create_if_not_exist=True)
db.create_db(BookDataFormatter)
# @todo почему не ругается?
# web = WebWithCache(config, random_sleep=True)
web = WebWithCache(config,random_sleep=True)

current_reader = Reader(login='', web_connection=web, db_connection=db, parser_html=ParserFromHTML, parser_db=ParserForDB)

# Есть ли пользователь на ЛЛ
login = input('Ввести логин \n')
# login = 'Eugenia_Novik'
if current_reader.exists(login=login):
    # # # если есть логин на ЛЛ
    print('Вы существуете!')
    print('Регистрируем вас, начинаем работу...')
    current_reader.register()
    # есть ли пользователь в БД?
    last_update = current_reader.has_db_entries()
    if last_update:
        # # если есть пользователь
        print(f'У вас есть записи от {last_update}!')
        # # # Скачать новые записи?
        update = input('Скачать записи заново?')
        if update == '1':
        # # # # Если скачать
            print('Записи будут скачены.')
            current_reader.update_books()
            print('Записи скачены.')
        else:
        # # # # Если не надо скачивать
            print('Записи не надо скачивать.')
    else:
    # # если нет пользователя в БД
        print('Начинаем скачивание...')
        current_reader.get_read_books_from_web()
        print('Скачивание завершено')
    print('Тут выдается файл для экспорта.')
    print('У вас книг ',len(current_reader.get_read_books_from_db()))
    # reader.create_export_file(type='csv')

else:
    # # # если нет логина на ЛЛ
    print('Вы не существуете!')



