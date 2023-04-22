import unittest

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.discover('.','test_*.py')
    print(tests)
    suite.addTests(tests)
    runner.run(suite)
