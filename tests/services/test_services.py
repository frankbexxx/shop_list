import unittest


@unittest.skip("Legacy Kivy service tests replaced by tests/test_app.py")
class LegacyServiceTests(unittest.TestCase):
    def test_legacy_suite_retired(self):
        self.assertTrue(True)
