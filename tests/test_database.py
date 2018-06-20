""" This module checks the database queries """

# Python import
import unittest
import os
import sqlite3
import uuid
import unittest.mock

# Project import
from labnote.utils import directory, database, conversion


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

            with self.assertRaises(sqlite3.Error):
                database.create_main_database()

    def test_protocols_database_creation(self):
        database.create_protocol_db()
        self.assertTrue(os.path.isfile(database.PROTOCOL_DATABASE_FILE_PATH))

    def test_protocols_database_creation_error(self):
        with unittest.mock.patch("sqlite3.connect") as mock_sqlite3_conn:
            mock_sqlite3_conn.side_effect = sqlite3.Error

            with self.assertRaises(sqlite3.Error):
                database.create_protocol_db()


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
        database.create_protocol_db()

    def tearDown(self):
        directory.cleanup_main_directory()

    def test_notebook_creation(self):
        database.create_notebook(self.nb_name, self.nb_uuid)

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notebook")

        self.assertEqual(cursor.fetchall(), [(conversion.uuid_bytes(self.nb_uuid), '{}'.format(self.nb_name))])

    def test_notebook_creation_error(self):
        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.create_notebook(self.nb_name, self.nb_uuid)

    def test_experiment_creation_data(self):
        database.create_notebook(self.nb_name, self.nb_uuid)

        database.create_experiment(self.exp_name, self.exp_uuid, self.exp_obj, str(self.nb_uuid))

        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiment")
        self.assertEqual(cursor.fetchall(), [(conversion.uuid_bytes(self.exp_uuid), '{}'.format(self.exp_name),
                                              conversion.uuid_bytes(self.nb_uuid), '{}'.format(self.exp_obj))])

    def test_experiment_creation_error(self):
        database.create_notebook(self.nb_name, self.nb_uuid)

        with unittest.mock.patch("labnote.utils.database.sqlite3.connect",
                                 unittest.mock.MagicMock(side_effect=sqlite3.Error)):

            with self.assertRaises(sqlite3.Error):
                database.create_experiment(self.exp_name, self.exp_uuid,
                                           self.exp_obj, str(self.nb_uuid))


class TestDatabaseSelectUpdateDelete(unittest.TestCase):
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
        database.create_protocol_db()
        database.create_notebook(self.nb_name, self.nb_uuid)
        database.create_experiment(self.exp_name, self.exp_uuid, self.exp_obj, str(self.nb_uuid))

    def tearDown(self):
        directory.cleanup_main_directory()

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
        cursor.execute("SELECT * FROM experiment")
        self.assertEqual(cursor.fetchall(), [(conversion.uuid_bytes(self.exp_uuid), '{}'.format(new_name),
                                              conversion.uuid_bytes(self.nb_uuid), '{}'.format(new_objective))])

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


if __name__ == '__main__':
    unittest.main()
