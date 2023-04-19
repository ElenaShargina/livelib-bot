from livelib import Urlparser
import unittest

class TestUrlparser(unittest.TestCase):
    def test_url_join(self):
        values=[
            [['foo'], 'foo'],
            [['foo/'], 'foo/'],
            # [[''],''],
            [['foo','bar'],'foo/bar'],
            [['foo/','bar','bum'], 'foo/bar/bum'],
            [['/foo','bar','bum/'], 'foo/bar/bum/'],
            [['http://www.example.com','foo/'], 'http://www.example.com/foo/']
        ]
        for i in values:
            with self.subTest(msg=f'Okey with {i[0]}'):
                up = Urlparser()
                self.assertEqual(i[1],up.url_join(*i[0]))

    def test_prefix_url_join(self):
        values = [
            {'site': 'http://www.example.com', 'urls': [''], 'correct': 'http://www.example.com'},
            {'site': 'http://www.example.com/', 'urls': ['foo'], 'correct': 'http://www.example.com/foo'},
            {'site': 'http://www.example.com', 'urls': ['foo', 'bar/'], 'correct': 'http://www.example.com/foo/bar/'},
            {'site':'http://www.example.com', 'urls':['foo','bar'], 'correct':'http://www.example.com/foo/bar'}
        ]
        for i in values:
            with self.subTest(msg=f'Okey at {i["site"]},{i["urls"]}'):
                up = Urlparser(i['site'])
                self.assertEqual(i['correct'],up.prefix_join(*i['urls']))




if __name__ == '__main__':
    unittest.main()
