import unittest


def test_suite():
    from mxmake.tests import test_hook
    from mxmake.tests import test_parser
    from mxmake.tests import test_templates
    from mxmake.tests import test_topics
    from mxmake.tests import test_utils

    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()

    suite.addTest(loader.loadTestsFromModule(test_hook))
    suite.addTest(loader.loadTestsFromModule(test_parser))
    suite.addTest(loader.loadTestsFromModule(test_templates))
    suite.addTest(loader.loadTestsFromModule(test_topics))
    suite.addTest(loader.loadTestsFromModule(test_utils))

    return suite


if __name__ == "__main__":
    import sys

    runner = unittest.TextTestRunner(failfast=True)
    result = runner.run(test_suite())
    sys.exit(not result.wasSuccessful())
