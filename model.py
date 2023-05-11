from livelib import *

config = Config('.env')
db = SQLite3Connection(config.db_config.sqlite_db)
web = WebWithCache(config, random_sleep=True)

login = input('Ввести логин')


# есть ли пользователь в БД?

# # если есть пользователь

# # # Скачать новые записи?

# # # # Если скачать

# # # # Если не надо скачивать

# # если нет пользователя

# # # если есть логин на ЛЛ

# # # если нет логина на ЛЛ



