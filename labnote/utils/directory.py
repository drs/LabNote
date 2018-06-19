# Python import
import os
import shutil

DEFAULT_MAIN_DIRECTORY_PATH = os.path.expanduser("~/Documents/LabNote")
NOTEBOOK_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/notebook")


def cleanup_main_directory():
    """ Delete the main directory """
    shutil.rmtree(DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)


def create_default_main_directory():
    """ Create the main directory at it's default location """

    # Create the defaults directories
    os.mkdir(DEFAULT_MAIN_DIRECTORY_PATH)
    os.mkdir(os.path.join(NOTEBOOK_DIRECTORY_PATH))


def create_nb_directory(nb_uuid):
    """ Create a directory for a new notebook

    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    # Create the notebook directory
    os.mkdir(notebook_path)


def delete_nb_directory(nb_uuid):
    """ Delete a notebook directory

    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    # Delete the notebook directory
    shutil.rmtree(notebook_path, ignore_errors=True)


def create_exp_directory(exp_uuid, nb_uuid):
    """ Create a directory for a new experiment

    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))

    # Create the experiment directory
    os.mkdir(experiment_path)
    os.mkdir(os.path.join(experiment_path + "/data"))


def delete_exp_directory(exp_uuid, nb_uuid):
    """ Delete an experiment directory

    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))

    # Delete the experiment directory
    shutil.rmtree(experiment_path, ignore_errors=True)
