# Python import
import os
import uuid
import unittest
import shutil
import unittest.mock

# Project import
from LabNote.data_management import database, directory, experiment


class TestExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.nb_uuid = uuid.uuid4()
        cls.exp_name = 'Experiment'
        cls.exp_obj = 'Experiment objective'
        cls.exp_uuid = uuid.uuid4()

    def setUp(self):
        directory.create_default_main_directory()
        directory.create_nb_directory(self.nb_uuid)
        directory.create_exp_directory(self.exp_uuid, self.nb_uuid)
        database.create_main_database()
        database.create_protocol_db()
        database.create_notebook(self.nb_name, self.nb_uuid)

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_create_empty_experiment(self):
        experiment.create_experiment(self.exp_uuid, self.nb_uuid, bytearray())
        self.assertTrue(os.path.isfile(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(self.nb_uuid)
                                       + "/{}".format(self.exp_uuid) + "/{}".format(self.exp_uuid))))

    def test_create_empty_experiment_oserror(self):
        with unittest.mock.patch('LabNote.data_management.experiment.open') as mock_open:
            mock_open.side_effect = OSError
            self.assertIsInstance(experiment.create_experiment(self.exp_uuid, self.nb_uuid, bytearray()), OSError)
