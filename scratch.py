from livelib import SimpleWeb
from livelib import Offline

of = Offline(site='http://www.fontanka.ru', encoding='utf-8', folder='test_offline')
f = of.get_page_text('http://www.fontanka.ru/')
print(f)
print(type(f))

