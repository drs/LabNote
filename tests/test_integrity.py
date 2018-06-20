""" This module checks the integrity module """

# Python import
import unittest
import os
import unittest.mock
import shutil
import sqlite3

# Project import
from labnote.utils import directory, database, fsentry, integrity


class TestIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.exp_name = 'Experiment'
        cls.exp_obj = 'Experiment objective'

    def setUp(self):
        fsentry.create_main_directory()
        fsentry.create_notebook(self.nb_name)

    def tearDown(self):
        fsentry.cleanup_main_directory()

    def test_full_check(self):
        self.assertFalse(integrity.IntegrityCheck().full_check())

    def test_full_check_create_main_directory(self):
        fsentry.cleanup_main_directory()
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_full_check_create_main_directory_notebook(self):
        fsentry.cleanup_main_directory()
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isdir(directory.NOTEBOOK_DIRECTORY_PATH))

    def test_full_check_create_main_directory_database(self):
        fsentry.cleanup_main_directory()
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isfile(database.MAIN_DATABASE_FILE_PATH))

    def test_full_check_create_main_directory_protocols_database(self):
        fsentry.cleanup_main_directory()
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isfile(database.PROTOCOL_DATABASE_FILE_PATH))

    def test_full_check_create_main_directory_oserror(self):
        fsentry.cleanup_main_directory()

        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            self.assertIs(integrity.IntegrityCheck().full_check()[1], integrity.FATAL_ERROR)

    def test_full_check_repair_main_directory_notebook(self):
        shutil.rmtree(directory.NOTEBOOK_DIRECTORY_PATH, ignore_errors=True)
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isdir(directory.NOTEBOOK_DIRECTORY_PATH))

    def test_full_check_repair_main_directory_notebook_oserror(self):
        shutil.rmtree(directory.NOTEBOOK_DIRECTORY_PATH, ignore_errors=True)
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            integrity.IntegrityCheck().full_check()
            self.assertIs(integrity.IntegrityCheck().full_check()[1], integrity.FATAL_ERROR)

    def test_full_check_repair_main_directory_database(self):
        os.remove(database.MAIN_DATABASE_FILE_PATH)
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isfile(database.MAIN_DATABASE_FILE_PATH))

    def test_full_check_repair_main_directory_database_oserror(self):
        os.remove(database.MAIN_DATABASE_FILE_PATH)

        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            integrity.IntegrityCheck().full_check()
            self.assertIs(integrity.IntegrityCheck().full_check()[1], integrity.FATAL_ERROR)

    def test_full_check_repair_main_directory_protocol_database(self):
        os.remove(database.PROTOCOL_DATABASE_FILE_PATH)
        integrity.IntegrityCheck().full_check()
        self.assertTrue(os.path.isfile(database.PROTOCOL_DATABASE_FILE_PATH))

    def test_full_check_repair_main_directory_protocol_database_oserror(self):
        os.remove(database.PROTOCOL_DATABASE_FILE_PATH)

        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            integrity.IntegrityCheck().full_check()
            self.assertIs(integrity.IntegrityCheck().full_check()[1], integrity.FATAL_ERROR)

    def test_full_check_database_connect_sqlite3_error(self):
        with unittest.mock.patch("labnote.utils.integrity.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            self.assertIs(integrity.IntegrityCheck().full_check()[1], integrity.FATAL_ERROR)

    def test_full_no_effect_main_directory_ok(self):
        integrity.IntegrityCheck().full_check()
        self.assertIs(len(os.listdir(directory.NOTEBOOK_DIRECTORY_PATH)), 1)


if __name__ == '__main__':
    unittest.main()