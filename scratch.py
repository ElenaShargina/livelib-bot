from livelib import *

import unittest

con = WebWithCache()
p = con.get_page_bs('http://www.livelib.ru/reader/Feana/read')
print(BSParser.all_books_from_page(p))


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