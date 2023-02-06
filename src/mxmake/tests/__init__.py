import unittest


def test_suite():
    from mxmake.tests import test_hook
    from mxmake.tests import test_parser
    from mxmake.tests import test_templates
    from mxmake.tests import test_topics
    from mxmake.tests import test_utils

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_hook))
    suite.addTest(unittest.findTestCases(test_parser))
    suite.addTest(unittest.findTestCases(test_templates))
    suite.addTest(unittest.findTestCases(test_topics))
    suite.addTest(unittest.findTestCases(test_utils))

    return suite


if __name__ == "__main__":
    import sys

    runner = unittest.TextTestRunner(failfast=True)
    result = runner.run(test_suite())
    sys.exit(not result.wasSuccessful())
