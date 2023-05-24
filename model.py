from livelib import *

# загружаем файл конфига
config = Config('.env')
# создаем связь с БД
db = SQLite3Connection(config, create_if_not_exist=True)
# создаем БД, если нужно
# db.create_db(BookDataFormatter)
# Создаем связь с сетью. Сайт ЛЛ очень медленный и там стоит защита от частых запросов,
# поэтому нужно задавать параметр случайных задержек random_sleep как True
web = WebWithCache(config,random_sleep=False)
# Создаем экспортера в xlsx.
xlsx_export = XLSXExport(config)

# Создаем текущего читателя, пока без логина. Логин спросим у пользователя.
current_reader = Reader(    login='',
                            web_connection=web,
                            db_connection=db,
                            parser_html=ParserFromHTML,
                            parser_db=ParserForDB,
                            parser_xlsx=ParserForXLSX,
                            export = xlsx_export
                        )

# Запрашиваем логин у пользователя
login = input('Ввести логин \n')
# login = 'Eugenia_Novik'
# @todo проверка на существоввние не срабатывает, изменение в html коде LL
if current_reader.exists(login=login):
    # # # если есть логин на ЛЛ
    print('Вы существуете!')
    print('Регистрируем вас, начинаем работу...')
    # регистрируем обращение пользователя
    current_reader.register()
    # Есть ли пользователь в БД?
    last_update = current_reader.has_db_entries()
    if last_update:
        # # если есть пользователь, выводим дату обновления записей
        print(f'У вас есть записи от {last_update}!')
        # # # Скачать новые записи?
        update = input('Скачать записи заново? (y)')
        if update == 'y':
        # Если надо скачать записи заново,
        # то удаляем имеющиеся записи и скачиваем всю информацию заново
            print('Записи будут скачены.')
            current_reader.update_books()
            print('Записи скачены.')
        else:
        # Если не надо скачивать, то ничего не делаем
            print('Записи не надо скачивать.')
    else:
    # если нет пользователя в БД, то обязательно нужно скачать все записи из сети
        print('Начинаем скачивание...')
        current_reader.get_read_books_from_web()
        print('Скачивание завершено')
    print('Тут выдается файл для экспорта.')
    print('У вас книг ',len(current_reader.get_read_books_from_db()))
    print(current_reader.create_export_xlsx_file())

else:
    # если нет логина на ЛЛ
    print('Вы не существуете!')



