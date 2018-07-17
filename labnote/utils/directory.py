# Python import
import os
import uuid

DEFAULT_MAIN_DIRECTORY_PATH = os.path.expanduser("~/Documents/LabNote")
NOTEBOOK_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/Notebook")
REFERENCES_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/References")
PROTOCOL_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/Protocols")
LIBRARY_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/Library")
PYTHON_LIBRARY_DIRECTORY_PATH = os.path.join(LIBRARY_DIRECTORY_PATH + "/python")
R_LIBRARY_DIRECTORY_PATH = os.path.join(LIBRARY_DIRECTORY_PATH + "/R")


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


def protocol_path(prt_uuid):
    """ Return the protocol path

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Protocol path
    """
    return os.path.join(PROTOCOL_DIRECTORY_PATH + "/{}".format(prt_uuid))


def protocol_resource_path(prt_uuid):
    """ Return the protocol resource directory path

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Protocol resource directory path
    """
    return os.path.join(protocol_path(prt_uuid) + "/resources")


def experiment_path(nb_uuid, exp_uuid):
    """ Return the experiment path

    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :return str: Experiment path
    """
    return os.path.join(notebook_path(nb_uuid) + "/{}".format(exp_uuid))


def experiment_resource_path(nb_uuid, exp_uuid):
    """ Return the experiment resource directory path

    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :return str: Experiment resource directory path
    """
    return os.path.join(experiment_path(nb_uuid, exp_uuid) + "/resources")
