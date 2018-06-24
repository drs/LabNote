""" This module test fsentry module """

# Python import
import unittest
import unittest.mock
import os
import sqlite3

# Project import
from labnote.utils import fsentry, directory, database, conversion


class TestFSEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.exp_name = 'Experiment'
        cls.exp_obj = 'Experiment objective'

    def setUp(self):
        fsentry.create_main_directory()

    def tearDown(self):
        fsentry.cleanup_main_directory()

    def test_cleanup_main_directory(self):
        fsentry.cleanup_main_directory()
        self.assertFalse(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_cleanup_main_directory_oserror(self):
        with unittest.mock.patch('shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.cleanup_main_directory()

    def test_create_main_directory(self):
        fsentry.cleanup_main_directory()
        fsentry.create_main_directory()
        self.assertTrue(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_create_main_directory_oserror(self):
        fsentry.cleanup_main_directory()

        with unittest.mock.patch('os.mkdir') as mock_rmtree:
            mock_rmtree.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.create_main_directory()

    def test_notebook_creation(self):
        fsentry.create_notebook(self.nb_name)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nb_name FROM notebook")

        self.assertEqual(cursor.fetchall()[0][0], self.nb_name)

    def test_notebook_creation_sqlite3_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                fsentry.create_notebook(self.nb_name)

    def test_integrity_check(self):
        fsentry.cleanup_main_directory()

        fsentry.check_integrity()
        self.assertTrue(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_integrity_sqlite_error(self):
        fsentry.cleanup_main_directory()

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                fsentry.check_integrity()

    def test_integrity_oserror(self):
        fsentry.cleanup_main_directory()

        with unittest.mock.patch('os.mkdir') as mock_rmtree:
            mock_rmtree.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.check_integrity()

