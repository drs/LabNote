# Python import
import unittest
import os
import uuid
import shutil
import unittest.mock
import errno

from PyQt5.QtWidgets import QApplication

# Project import
from LabNote.data_management import directory

app = QApplication([])


class TestMainDirectoryCreation(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_main_directory_creation(self):
        directory.create_default_main_directory()
        self.assertTrue(os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH))

    def test_main_directory_creation_error(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError
            ret = directory.create_default_main_directory()
            self.assertIsInstance(ret, OSError)


class TestSubdirectoryCreation(unittest.TestCase):
    def setUp(self):
        directory.create_default_main_directory()

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_main_notebook_directory_creation(self):
        self.assertTrue(os.path.isdir(directory.NOTEBOOK_DIRECTORY_PATH))

    def test_notebook_directory_creation(self):
        # Create a directory
        nb_uuid = uuid.uuid4()
        directory.create_nb_directory(nb_uuid)
        self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))))

    def test_notebook_directory_creation_raise_oserror(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError
            nb_uuid = uuid.uuid4()
            self.assertIsInstance(directory.create_nb_directory(nb_uuid), OSError)

    def test_notebook_directory_creation_oserror_no_notebook(self):
        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError
            nb_uuid = uuid.uuid4()
            directory.create_nb_directory(nb_uuid)
            self.assertFalse(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/" + str(nb_uuid))))

    def test_experiment_directory_creation(self):
        nb_uuid = uuid.uuid4()
        directory.create_nb_directory(nb_uuid)
        exp_uuid = uuid.uuid4()
        directory.create_exp_directory(exp_uuid, nb_uuid)
        self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH +
                                                   "/{}".format(nb_uuid) + "/{}".format(exp_uuid))))

    def test_experiment_resources_directory_creation(self):
        nb_uuid = uuid.uuid4()
        directory.create_nb_directory(nb_uuid)
        exp_uuid = uuid.uuid4()
        directory.create_exp_directory(exp_uuid, nb_uuid)
        self.assertTrue(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH +
                                                   "/{}".format(nb_uuid) + "/{}".format(exp_uuid) + "/resources")))

    def test_experiment_directory_creation_error(self):
        nb_uuid = uuid.uuid4()
        directory.create_nb_directory(nb_uuid)

        with unittest.mock.patch('os.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError
            exp_uuid = uuid.uuid4()
            self.assertIsInstance(directory.create_exp_directory(exp_uuid, nb_uuid), OSError)

class TestDirectoryDeletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb_name = 'Notebook'
        cls.nb_uuid = uuid.uuid4()

    def setUp(self):
        directory.create_default_main_directory()
        directory.create_nb_directory(self.nb_uuid)

    def tearDown(self):
        shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)

    def test_notebook_directory_deletion(self):
        directory.delete_nb_directory(self.nb_uuid)
        self.assertFalse(os.path.isdir(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(self.nb_uuid))))

    def test_notebook_directory_deletion_oserror(self):
        with unittest.mock.patch('shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = OSError
            self.assertIsInstance(directory.delete_nb_directory(self.nb_uuid), OSError)


if __name__ == '__main__':
    unittest.main()
