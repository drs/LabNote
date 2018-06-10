# Python import
import unittest
import os
import sqlite3
import uuid
import unittest.mock

from PyQt5.QtWidgets import QApplication

# Project import
from LabNote.data_management import directory, database

app = QApplication([])

SILENT_TESTING = True


class TestDatabaseCreation(unittest.TestCase):
    def setUp(self):
        directory.create_default_main_directory()

    def tearDown(self):
        directory.cleanup_main_directory()

    def test_main_database_creation(self):
        database.create_main_database()
        self.assertTrue(os.path.isfile(database.MAIN_DATABASE_FILE_PATH))

    def test_main_database_creation_sqlite_error(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error
            self.assertIsInstance(database.create_main_database(), sqlite3.Error)

    def test_main_database_creation_cleanup(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error
            database.create_main_database()
            self.assertFalse(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_protocols_database_creation(self):
        database.create_protocol_db()
        self.assertTrue(os.path.isfile(database.PROTOCOL_DATABASE_FILE_PATH))

    def test_protocols_database_creation_error(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error
            self.assertIsInstance(database.create_protocol_db(), sqlite3.Error)

    def test_protocols_database_creation_cleanup(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error
            database.create_protocol_db()
            self.assertFalse(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))


class TestDatabaseInsert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.nb_uuid = uuid.uuid4()

    def setUp(self):
        directory.create_default_main_directory()
        database.create_main_database()
        database.create_protocol_db()

    def tearDown(self):
        directory.cleanup_main_directory()

    def test_notebook_creation(self):
        with unittest.mock.patch("LabNote.data_management.database.sqlite3") as mock_sqlite3:
            database.create_notebook(self.nb_name, self.nb_uuid)
            mock_sqlite3.connect().cursor().execute.assert_called_with(
                "\nINSERT INTO notebook (name, uuid) VALUES ('{}', '{}')\n".format(self.nb_name, self.nb_uuid))

    def test_notebook_creation_error(self):
        with unittest.mock.patch("LabNote.data_management.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            self.assertIsInstance(database.create_notebook(self.nb_name, self.nb_uuid), sqlite3.Error)


class TestDatabaseSelect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.nb_uuid = uuid.uuid4()

    def setUp(self):
        directory.create_default_main_directory()
        database.create_main_database()
        database.create_protocol_db()
        database.create_notebook(self.nb_name, self.nb_uuid)

    def tearDown(self):
        directory.cleanup_main_directory()

    def test_notebook_selection(self):
        with unittest.mock.patch("LabNote.data_management.database.sqlite3") as mock_sqlite3:
            database.get_notebook_list()
            mock_sqlite3.connect().cursor().execute.assert_called_with(database.SELECT_NOTEBOOK_NAME.format(
                self.nb_name, self.nb_uuid))

    def test_notebook_selection_results(self):
        result = database.get_notebook_list()
        self.assertEqual(result, [{'id': 1, 'name': 'Notebook'}])


if __name__ == '__main__':
    unittest.main()
