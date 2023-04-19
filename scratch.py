from livelib import *

r = Reader('qwerty5677890', connection=Offline(folder='offline',encoding='utf-8'), bsparser=BSParser() )
print(r.get_main_page())

