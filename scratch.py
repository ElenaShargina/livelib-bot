from livelib import *

import unittest

from livelib.parser import BookDataFormatter

# Eugenia_Novik
# Feana
# Kasssiopei - 60 read books
# ElviraYakovleva - 11 read books
# Shakespeare - 2096 read books

# r = Reader('Shakespeare',WebWithCache(site='https://www.livelib.ru', random_sleep = True))
# res = r.get_all_read_books()
# print(res)


s = SQLite3Connection('db/first.db')
formatter = BookDataFormatter
# print(formatter.common_db())
# print([i['db'] for i in formatter.common.values()])
# s.create_table('Books', formatter.common_db())
print(s.run_single_sql('PRAGMA table_info(Books)'))
# s.create_tables()




# r = Reader('qwerty5677890', connection=WebWithCache(folder='cache',encoding='utf-8'), bsparser=BSParser() )
# print(r.get_main_page())


# def func1(x):
#     print('func1')
#     try:
#         if x:
#             print('exception from func1')
#             raise Exception('My lovely Exception')
#         else:
#             return 100
#     except Exception as exc:
#         raise Exception('exception from func')
#
# def func2(x):
#     print('func2')
#     try:
#         return func1(x)
#     except Exception as exc:
#         print('exception from func2')
#         raise Exception('exception from func2')
#         return 200
#
# # print(func2(True))
#
# class st(unittest.TestCase):
#     def test_1(self):
#        self.assertEqual(100,func2(False))
#        with self.assertRaises(Exception):
#             func2(True)

# unittest.main()