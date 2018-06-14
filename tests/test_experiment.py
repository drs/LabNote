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

    def test_encode_experiment(self):
        html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"><html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; }</style></head><body style=" font-family:'.SF NS Text'; font-size:13pt; font-weight:400; font-style:normal;"><p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>"""
        expected = b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"><html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; }</style></head><body style=" font-family:\'.SF NS Text\'; font-size:13pt; font-weight:400; font-style:normal;"><p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>'
        encoded_html = experiment.encode_experiment(html)
        self.assertEqual(encoded_html, expected)

    def test_create_empty_experiment(self):
        experiment.write_experiment(self.exp_uuid, self.nb_uuid, bytes())
        self.assertTrue(os.path.isfile(os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(self.nb_uuid)
                                       + "/{}".format(self.exp_uuid) + "/{}".format(self.exp_uuid))))

    def test_create_empty_experiment_oserror(self):
        with unittest.mock.patch('LabNote.data_management.experiment.open') as mock_open:
            mock_open.side_effect = OSError
            self.assertIsInstance(experiment.write_experiment(self.exp_uuid, self.nb_uuid, bytearray()), OSError)

    def test_open_experiment(self):
        html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"><html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; }</style></head><body style=" font-family:'.SF NS Text'; font-size:13pt; font-weight:400; font-style:normal;"><p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>"""
        experiment.write_experiment(self.exp_uuid, self.nb_uuid, experiment.encode_experiment(html))
        self.assertEqual(experiment.read_experiment(self.exp_uuid, self.nb_uuid), html)