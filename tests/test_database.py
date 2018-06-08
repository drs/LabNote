# Python import
import unittest
import os
import sqlite3
import shutil
import unittest.mock
import errno

from PyQt5.QtWidgets import QApplication

# Project import
from LabNote.data_management import directory, database
from LabNote.common import logs

app = QApplication([])

SILENT_TESTING = True


class TestDatabaseCreation(unittest.TestCase):
    def setUp(self):
        directory.create_default_main_directory()

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_main_database_creation(self):
        database.create_main_database()
        self.assertTrue(os.path.isfile(database.MAIN_DATABASE_FILE_PATH))

    def test_main_database_creation_sqlite_error(self):
        with self.assertRaises(sqlite3.Error):
            with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
                mock_sqlite3_conn.side_effect = sqlite3.Error
                database.create_main_database(silent=SILENT_TESTING)

    def test_main_database_creation_cleanup(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error
            try:
                database.create_main_database(silent=SILENT_TESTING)
            except sqlite3.Error:
                self.assertFalse(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_protocols_database_creation(self):
        database.create_protocol_db()
        self.assertTrue(os.path.isfile(database.PROTOCOL_DATABASE_FILE_PATH))

    def test_protocols_database_creation_error(self):
        with self.assertRaises(sqlite3.Error):
            with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
                mock_sqlite3_conn.side_effect = sqlite3.Error
                database.create_protocol_db(silent=SILENT_TESTING)

    def test_protocols_database_creation_cleanup(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error
            try:
                database.create_protocol_db(silent=SILENT_TESTING)
            except sqlite3.Error:
                self.assertFalse(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))



if __name__ == '__main__':
    unittest.main()
