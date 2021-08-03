import unittest

from fastapi.testclient import TestClient

from Quadrant import app
from Quadrant.migrations import db_utils
from tests.utils import clean_tests_folders, create_test_folders, make_async_call


class TestUserAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        create_test_folders()
        db_utils.initialize_db()

    def setUp(self) -> None:
        self.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        db_utils.drop_db()
        clean_tests_folders()
