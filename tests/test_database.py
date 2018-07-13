""" This module checks the database queries """

# Python import
import unittest
import os
import sqlite3
import uuid
import unittest.mock

# Project import
from labnote.utils import directory, database, conversion, fsentry


class TestDatabaseCreation(unittest.TestCase):
    def setUp(self):
        directory.create_default_main_directory()

    def tearDown(self):
        fsentry.cleanup_main_directory()

    def test_main_database_creation(self):
        database.create_main_database()
        self.assertTrue(os.path.isfile(database.MAIN_DATABASE_FILE_PATH))

    def test_main_database_creation_sqlite_error(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error

            with self.assertRaises(sqlite3.Error):
                database.create_main_database()


class TestDatabaseInsert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.nb_uuid = uuid.uuid4()
        cls.exp_name = 'Experiment'
        cls.exp_obj = 'Experiment objective'
        cls.exp_uuid = uuid.uuid4()

    def setUp(self):
        directory.create_default_main_directory()
        database.create_main_database()

    def tearDown(self):
        fsentry.cleanup_main_directory()

    def test_notebook_creation(self):
        database.create_notebook(self.nb_name, self.nb_uuid)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notebook")

        self.assertEqual(cursor.fetchall(), [(conversion.uuid_bytes(self.nb_uuid), 'Notebook', None)])

    def test_notebook_creation_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.create_notebook(self.nb_name, self.nb_uuid)

    def test_experiment_creation(self):
        database.create_notebook(self.nb_name, self.nb_uuid)

        database.create_experiment(self.exp_name, self.exp_uuid, self.exp_obj, str(self.nb_uuid))

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT exp_uuid, name, nb_uuid, objective FROM experiment")

        self.assertEqual(cursor.fetchall(), [(conversion.uuid_bytes(self.exp_uuid),
                                              self.exp_name,
                                              conversion.uuid_bytes(self.nb_uuid),
                                              self.exp_obj)])

    def test_experiment_creation_error(self):
        database.create_notebook(self.nb_name, self.nb_uuid)

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.create_experiment(self.exp_name, self.exp_uuid,
                                           self.exp_obj, str(self.nb_uuid))

    def test_category_creation(self):
        name = 'Category'
        database.insert_category(name)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM category")

        self.assertEqual(cursor.fetchall(), [(name,)])

    def test_category_creation_error(self):
        name = 'Category'

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.insert_category(name)

    def test_subcategory_creation(self):
        category_name = 'Category'
        name = 'Subcategory'

        database.insert_category(category_name)
        database.insert_subcategory(name, 1)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, category_id FROM subcategory")

        self.assertEqual(cursor.fetchall(), [(name, 1)])

    def test_subcategory_creation_error(self):
        category_name = 'Category'
        name = 'Subcategory'

        database.insert_category(category_name)

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.insert_subcategory(name, 1)


class TestDatabaseSelectUpdateDelete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.nb_uuid = uuid.uuid4()
        cls.exp_name = 'Experiment'
        cls.exp_obj = 'Experiment objective'
        cls.exp_uuid = uuid.uuid4()
        cls.category = 'Category'
        cls.subcategory = 'Subcategory'

    def setUp(self):
        directory.create_default_main_directory()
        database.create_main_database()
        database.create_notebook(self.nb_name, self.nb_uuid)
        database.create_experiment(self.exp_name, self.exp_uuid, self.exp_obj, str(self.nb_uuid))
        database.insert_category(self.category)
        database.insert_subcategory(self.subcategory, 1)

    def tearDown(self):
        fsentry.cleanup_main_directory()

    def test_notebook_select(self):
        result = database.get_notebook_list()
        self.assertEqual(result, [{'uuid': str(self.nb_uuid), 'name': '{}'.format(self.nb_name)}])

    def test_notebook_select_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.get_notebook_list()

    def test_notebook_update(self):
        new_name = "Notebook 1"
        database.update_notebook(new_name, str(self.nb_uuid))

        result = database.get_notebook_list()
        self.assertEqual(result, [{'uuid': '{}'.format(self.nb_uuid), 'name': '{}'.format(new_name)}])

    def test_notebook_update_error(self):
        new_name = "Notebook 1"
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.update_notebook(new_name, str(self.nb_uuid))

    def test_notebook_delete(self):
        database.delete_notebook(str(self.nb_uuid))
        database.get_notebook_list()

        result = database.get_notebook_list()
        self.assertEqual(result, [])

    def test_notebook_delete_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.delete_notebook(str(self.nb_uuid))

    def test_notebook_experiment_select(self):
        result = database.get_experiment_list_notebook(str(self.nb_uuid))
        self.assertEqual(result, [{'uuid': '{}'.format(self.exp_uuid), 'name': '{}'.format(self.exp_name),
                         'objective': '{}'.format(self.exp_obj)}])

    def test_notebook_experiment_select_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.get_experiment_list_notebook(str(self.nb_uuid))

    def test_select_experiment(self):
        result = database.get_experiment_informations(str(self.exp_uuid))
        self.assertEqual(result, {'name': self.exp_name, 'objective': self.exp_obj})

    def test_select_experiment_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.get_experiment_informations(str(self.exp_uuid))

    def test_update_experiment(self):
        new_name = 'Experiment 1'
        new_objective = 'Updated objective'
        database.update_experiment(str(self.exp_uuid), new_name, new_objective)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT exp_uuid, name, nb_uuid, objective FROM experiment")
        self.assertEqual(cursor.fetchall(), [(conversion.uuid_bytes(self.exp_uuid),
                                             new_name,
                                              conversion.uuid_bytes(self.nb_uuid),
                                              new_objective)])

    def test_update_experiment_error(self):
        new_name = 'Experiment 1'
        new_objective = 'Updated objective'

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.update_experiment(str(self.exp_uuid), new_name, new_objective)

    def test_delete_experiment(self):
        database.delete_experiment(str(self.exp_uuid))

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiment")
        self.assertEqual(cursor.fetchall(), [])

    def test_delete_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.delete_experiment(str(self.exp_uuid))

    def test_update_category(self):
        name = 'Category 1'
        database.update_category(name, 1)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM category")

        self.assertEqual(cursor.fetchall(), [(name,)])

    def test_update_category_error(self):
        name = 'Category 1'

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                database.update_category(name, 1)

    def test_insert_duplicate_category_error(self):
        with self.assertRaises(sqlite3.IntegrityError):
            database.insert_category(self.category)

    def test_delete_category(self):
        database.delete_subcategory(1)
        database.delete_category(1)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM category")

        self.assertEqual(cursor.fetchall(), [])

    def delete_category_foreign_key_error(self):
        with self.assertRaises(sqlite3.Error):
            database.delete_category(1)

    def test_delete_category_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                database.delete_category(1)

    def test_update_subcategory(self):
        name = 'Subcategory 1'

        database.update_subcategory(name, 1, 1)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, category_id FROM subcategory")

        self.assertEqual(cursor.fetchall(), [(name, 1)])

    def test_update_subcategory_error(self):
        name = 'Subcategory 1'

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                database.update_subcategory(name, 1, 1)

    def test_insert_duplicate_subcategory_error(self):
        with self.assertRaises(sqlite3.IntegrityError):
            database.insert_subcategory(self.subcategory, 1)

    def test_delete_subcategory(self):
        database.delete_subcategory(1)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM subcategory")

        self.assertEqual(cursor.fetchall(), [])

    def test_delete_subcategory_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):
            with self.assertRaises(sqlite3.Error):
                database.delete_subcategory(1)


if __name__ == '__main__':
    unittest.main()
