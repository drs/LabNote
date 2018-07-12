""" This module contains all the functions used to handle files """

# Python import
import os
import shutil
import uuid

# Project import
from labnote.utils import directory


def copy_file_to_data(nb_uuid, exp_uuid, path):
    """ Move a file to an experiment data folder

    :param nb_uuid: UUID of the notebook that contains the experiment
    :type nb_uuid: str
    :param exp_uuid: Experiment UUID
    :type exp_uuid: str
    :param path: Path of the file to copy
    :param path: str
    """

    notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))
    data_path = os.path.join(experiment_path + "/data")

    file_uuid = uuid.uuid4()

    data_file = os.path.join(data_path + "/{}".format(file_uuid))

    try:
        shutil.copy2(path, data_file)
    except OSError as exception:
        return exception


def copy_dataset(dt_uuid, nb_uuid, path):
    """ Copy a dataset """
    file_name = dataset_excel_file(dt_uuid=dt_uuid, nb_uuid=nb_uuid)
    shutil.copy2(path, file_name)


def reference_file_path(ref_uuid):
    """ Return the path to a reference file

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    """
    return os.path.join(directory.REFERENCES_DIRECTORY_PATH + "/{}.pdf".format(ref_uuid))


def dataset_excel_file(dt_uuid, nb_uuid):
    """ Return a dataset file path

    :param dt_uuid: Dataset UUID
    :type dt_uuid: str
    :param nb_uuid: Notebook UUID
    :type nb_uuid: str
    """
    return os.path.join(directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid) + "/{}.xlsx".format(dt_uuid))
