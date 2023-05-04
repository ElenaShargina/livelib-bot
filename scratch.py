from livelib import *

import unittest

r = Reader('feana',WebWithCache())
res = r.get_books_from_page('http://www.livelib.ru/reader/Feana/read/listview/smalllist/~3')
print(res)



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