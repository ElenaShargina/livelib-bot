from livelib import SimpleWeb
from livelib import Offline

of = Offline(site='http://www.livelib.ru')
of.create_file('http://www.livelib.ru/foo/bar')
of.create_file('http://www.livelib.ru/foo/bar.html')
of.create_file('http://www.livelib.ru/foo/2')
of.create_file('http://www.livelib.ru/foo/bar/')
of.create_file('http://www.livelib.ru/foo/bar/1.htm')