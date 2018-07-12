# Python import
import os

DEFAULT_MAIN_DIRECTORY_PATH = os.path.expanduser("~/Documents/LabNote")
NOTEBOOK_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/Notebook")
REFERENCES_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/References")


def notebook_path(nb_uuid):
    """ Return the notebook path for the given UUID

    :param nb_uuid: Notebook UUID
    :type nb_uuid: str
    :return str: Notebook path
    """
    return os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))


def dataset_notebook_path(nb_uuid):
    """ Return the notebook dataset folder path

    :param nb_uuid: Notebook UUID
    :type nb_uuid: str
    :return str: Notebook dataset path
    """
    return os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid) + "/Dataset")


def dataset_path(nb_uuid, dt_uuid):
    """ Return the dataset folder path

    :param nb_uuid: Notebook UUID
    :type nb_uuid: str
    :param dt_uuid: Dataset UUID
    :type dt_uuid: str
    :return str: Dataset path
    """
    return os.path.join(dataset_notebook_path(nb_uuid=nb_uuid) + "/{}".format(dt_uuid))