import unittest
import test_reader, test_bsparser, test_connection, test_urlparser

# class All(unittest.TestSuite):
#     tests = [test_reader,test_bsparser]

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for test_class in [test_reader.Test_Reader,
                       test_bsparser.Test_BSParser,
                        test_urlparser.TestUrlparser,
                       test_connection.Test_WebWithCache,
                       test_connection.Test_SimpleWeb]:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    runner.run(suite)
