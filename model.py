from livelib import *

# загружаем файл с конфигурационными данными
config = Config('.env')

# Создаем текущего читателя, пока без логина. Логин спросим у пользователя.
current_reader = Reader(login='',
                        web_connection=WebWithCache(config, random_sleep=False),
                        db_connection=SQLite3Connection(config, create_if_not_exist=True),
                        parser_html=ParserFromHTML,
                        parser_db=ParserForDB,
                        parser_xlsx=ParserForXLSX,
                        export=XLSXExport(config)
                        )

# Запрашиваем логин у пользователя
login = input('Ввести логин \n')
# Примеры существующих логинов пользователей, для тестирования можно расскоментировать строчку
# login = 'Eugenia_Novik'
# login = 'Humming_Bird'
# login = 'Kasssiopei'

if current_reader.exists(login=login):
    # # # если этот логин есть на ЛЛ
    print('Вы найдены на ЛЛ!')
    print('Регистрируем вас, начинаем работу...')
    # регистрируем пользователя в нашей БД
    current_reader.register()
    # Теперь включаем задержку обращения к сайту, чтобы он не выдал отказ при частых запросах.
    current_reader.web_connection.random_sleep = True
    # Есть ли пользователь в БД?
    last_update = current_reader.has_db_entries()
    if last_update:
        # @todo формат времени на человеческий
        # @todo количество записей тоже указать?
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
    print('У вас книг ', len(current_reader.get_read_books_from_db()))
    print(current_reader.create_export_xlsx_file())

else:
    # если нет логина на ЛЛ
    print('Вы не найден на ЛЛ!')
