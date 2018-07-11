""" This module test fsentry module """

# Python import
import unittest
import unittest.mock
import os
import sqlite3
import uuid

# Project import
from labnote.utils import fsentry, database, files, directory
from labnote.core import data
from labnote.interface import library


class TestFSEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.exp_name = 'Experiment'
        cls.exp_obj = 'Experiment objective'
        cls.exp_uuid = str(uuid.uuid4())
        cls.reference_key = 'reference'
        cls.reference_uuid = str(uuid.uuid4())
        cls.category = 'Category'
        cls.subcategory = 'Subcategory'
        cls.project_name = 'Project'

    def setUp(self):
        fsentry.create_main_directory()
        database.insert_ref_category(self.category)
        database.insert_ref_subcategory(self.subcategory, 1)
        database.insert_ref(data.uuid_bytes(self.reference_uuid), self.reference_key, library.TYPE_ARTICLE, 1)
        database.insert_project(self.project_name)

    def tearDown(self):
        fsentry.cleanup_main_directory()

    def test_add_reference_pdf_file(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)
        self.assertTrue(os.path.isfile(files.reference_file_path(self.reference_uuid)))

    def test_add_reference_pdf_database(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ref_uuid, file_attached FROM refs")

            self.assertEqual(cursor.fetchall(), [(data.uuid_bytes(self.reference_uuid), True)])

    def test_add_reference_database_error(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                fsentry.add_reference_pdf(self.reference_uuid, file_path)

    def test_add_reference_oserror(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")

        with unittest.mock.patch('shutil.copy2') as mock_shutil:
            mock_shutil.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.add_reference_pdf(self.reference_uuid, file_path)

    def test_add_reference_oserror_cleanup(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")

        with unittest.mock.patch('shutil.copy2') as mock_shutil:
            mock_shutil.side_effect = OSError

            try:
                fsentry.add_reference_pdf(self.reference_uuid, file_path)
            except OSError:
                pass

            with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ref_uuid, file_attached FROM refs")

                self.assertEqual(cursor.fetchall(), [(data.uuid_bytes(self.reference_uuid), 0)])

    def test_delete_reference_pdf_file(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)

        fsentry.delete_reference_pdf(self.reference_uuid)
        self.assertFalse(os.path.isfile(files.reference_file_path(self.reference_uuid)))

    def test_delete_reference_pdf_database(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)

        fsentry.delete_reference_pdf(self.reference_uuid)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ref_uuid, file_attached FROM refs")

            self.assertEqual(cursor.fetchall(), [(data.uuid_bytes(self.reference_uuid), False)])

    def test_delete_reference_database_error(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                fsentry.delete_reference_pdf(self.reference_uuid)

    def test_delete_reference_oserror(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)

        with unittest.mock.patch('os.remove') as mock_remove:
            mock_remove.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.delete_reference_pdf(self.reference_uuid)

    def test_delete_reference_oserror_cleanup(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/resources/blank.pdf")
        fsentry.add_reference_pdf(self.reference_uuid, file_path)

        with unittest.mock.patch('os.remove') as mock_remove:
            mock_remove.side_effect = OSError

            try:
                fsentry.delete_reference_pdf(self.reference_uuid)
            except OSError:
                pass

            with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ref_uuid, file_attached FROM refs")

                self.assertEqual(cursor.fetchall(), [(data.uuid_bytes(self.reference_uuid), True)])

    def test_create_notebook_database(self):
        fsentry.create_notebook(self.nb_name, 1)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM notebook")

            self.assertEqual(cursor.fetchall(), [(self.nb_name,)])

    def test_create_notebook_directory(self):
        fsentry.create_notebook(self.nb_name, 1)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nb_uuid FROM notebook")

            uuid = data.uuid_string(cursor.fetchall()[0][0])
            self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(uuid))))

    def test_create_notebook_database_error(self):
        with unittest.mock.patch("labnote.utils.fsentry.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                fsentry.create_notebook(self.nb_name, 1)

    def test_create_notebook_directory_error(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.create_notebook(self.nb_name, 1)

    def test_create_notebook_duplicate_error(self):
        fsentry.create_notebook(self.nb_name, 1)
        with self.assertRaises(sqlite3.Error):
            fsentry.create_notebook(self.nb_name, 1)

    def test_create_notebook_directory_error_cleanup(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            try:
                fsentry.create_notebook(self.nb_name, 1)
            except OSError:
                pass

            with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM notebook")

                self.assertEqual(cursor.fetchall(), [])

    def test_delete_notebook_database(self):
        fsentry.create_notebook(self.nb_name, 1)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nb_uuid FROM notebook")

            uuid = data.uuid_string(cursor.fetchall()[0][0])

        fsentry.delete_notebook(uuid)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM notebook")

            self.assertEqual(cursor.fetchall(), [])

    def test_delete_notebook_directory(self):
        fsentry.create_notebook(self.nb_name, 1)

        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nb_uuid FROM notebook")

            uuid = data.uuid_string(cursor.fetchall()[0][0])

        fsentry.delete_notebook(uuid)

        self.assertFalse(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(uuid))))

    def test_delete_notebook_database_error(self):
        fsentry.create_notebook(self.nb_name, 1)
        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nb_uuid FROM notebook")

            uuid = data.uuid_string(cursor.fetchall()[0][0])

        with unittest.mock.patch("labnote.utils.fsentry.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                fsentry.delete_notebook(uuid)

    def test_cdelete_notebook_directory_error(self):
        fsentry.create_notebook(self.nb_name, 1)
        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nb_uuid FROM notebook")

            uuid = data.uuid_string(cursor.fetchall()[0][0])

        with unittest.mock.patch('shutil.rmtree') as mock_shutil:
            mock_shutil.side_effect = OSError

            with self.assertRaises(OSError):
                fsentry.delete_notebook(uuid)

    def test_delete_notebook_directory_error_cleanup(self):
        fsentry.create_notebook(self.nb_name, 1)
        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nb_uuid FROM notebook")

            uuid = data.uuid_string(cursor.fetchall()[0][0])

        with unittest.mock.patch('shutil.rmtree') as mock_shutil:
            mock_shutil.side_effect = OSError

            try:
                fsentry.delete_notebook(uuid)
            except OSError:
                pass

            with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM notebook")

                self.assertEqual(cursor.fetchall(), [(self.nb_name,)])
