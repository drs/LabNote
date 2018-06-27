""" This module checks the directory management """

# Python import
import unittest
import os
import uuid
import shutil
import unittest.mock

# Project import
from labnote.utils import directory


class TestMainDirectoryCreation(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_main_directory_creation(self):
        directory.create_default_main_directory()
        self.assertTrue(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_main_directory_creation_error(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError

            with self.assertRaises(OSError):
                directory.create_default_main_directory()


class TestSubdirectoryCreation(unittest.TestCase):
    def setUp(self):
        directory.create_default_main_directory()

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_main_notebook_directory_creation(self):
        self.assertTrue(os.path.isdir(directory.NOTEBOOK_DIRECTORY_PATH))

    def test_main_references_directory_creation(self):
        self.assertTrue(os.path.isdir(directory.REFERENCES_DIRECTORY_PATH))

    def test_notebook_directory_creation(self):
        # Create a directory
        nb_uuid = str(uuid.uuid4())
        directory.create_nb_directory(nb_uuid)
        self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))))

    def test_notebook_directory_creation_raises(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError
            nb_uuid = str(uuid.uuid4())

            with self.assertRaises(OSError):
                directory.create_nb_directory(nb_uuid)


class TestExperimentDirectoryCreation(unittest.TestCase):
    def setUp(self):
        directory.create_default_main_directory()
        self.nb_uuid = str(uuid.uuid4())
        directory.create_nb_directory(self.nb_uuid)

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_experiment_directory_creation(self):
        exp_uuid = str(uuid.uuid4())
        directory.create_exp_directory(exp_uuid, self.nb_uuid)
        self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH +
                                                   "/{}".format(self.nb_uuid) + "/{}".format(exp_uuid))))

    def test_experiment_resources_directory_creation(self):
        exp_uuid = str(uuid.uuid4())
        directory.create_exp_directory(exp_uuid, self.nb_uuid)
        self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH +
                                                   "/{}".format(self.nb_uuid) + "/{}".format(exp_uuid) + "/data")))

    def test_experiment_directory_creation_error(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError
            exp_uuid = str(uuid.uuid4())

            with self.assertRaises(OSError):
                directory.create_exp_directory(exp_uuid, self.nb_uuid)


class TestDirectoryDeletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_uuid = str(uuid.uuid4())
        cls.exp_uuid = str(uuid.uuid4())

    def setUp(self):
        directory.create_default_main_directory()
        directory.create_nb_directory(self.nb_uuid)
        directory.create_exp_directory(self.exp_uuid, self.nb_uuid)

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_notebook_directory_deletion(self):
        directory.delete_nb_directory(self.nb_uuid)
        self.assertFalse(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(self.nb_uuid))))

    def test_notebook_directory_deletion_oserror(self):
        with unittest.mock.patch('shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = OSError

            with self.assertRaises(OSError):
                directory.delete_nb_directory(self.nb_uuid)

    def test_experiment_directory_deletion(self):
        directory.delete_exp_directory(self.exp_uuid, self.nb_uuid)
        self.assertFalse(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(self.nb_uuid) +
                                                    "/{}".format(self.exp_uuid))))

    def test_experiment_directory_deletion_oserror(self):
        with unittest.mock.patch('shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = OSError

            with self.assertRaises(OSError):
                directory.delete_exp_directory(self.exp_uuid, self.nb_uuid)


if __name__ == '__main__':
    unittest.main()
