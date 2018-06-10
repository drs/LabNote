# Python import
import os
import logging
import shutil

# Project import
from LabNote.common import logs

DEFAULT_MAIN_DIRECTORY_PATH = logs.DEFAULT_MAIN_DIRECTORY_PATH # This is required to avoid double dependancy
NOTEBOOK_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/notebook")


def cleanup_main_directory():
    """ Delete the main directory

    .. note:
        This fonction is used to cleanup the main directory when an error occur during the creation of the main
        directory
    """
    shutil.rmtree(DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)


def create_default_main_directory():
    """ Create the main directory at it's default location

    :returns: An exception if an exception occured
    """

    # Create the defaults directories
    try:
        os.mkdir(DEFAULT_MAIN_DIRECTORY_PATH)
        os.mkdir(os.path.join(NOTEBOOK_DIRECTORY_PATH))
        os.mkdir(logs.LOG_DIRECTORY_PATH)
    except OSError as exception:
        # Warn the user about the error
        # This is a fatal error as the program cannot continue without a basic file structure

        # Try to cleanup the main directory
        try:
            cleanup_main_directory()
        except:
            pass  # No need to raise any exception as an error message is already shown to the user

        return exception


def create_nb_directory(nb_name, nb_uuid):
    """ Create a directory for a new notebook

    :param nb_name: Notebook name
    :type nb_name: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :returns: An exception if an exception occured
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    try:
        os.mkdir(notebook_path)
    except OSError as exception:
        #  Log the exception
        logging.info("Creating a directory for a notebook ({})".format(nb_name))
        logging.exception(str(exception))

        return exception


def delete_nb_directory(nb_name, nb_uuid):
    """ Delete a notebook directory

    :param nb_name: Notebook name
    :type nb_name: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :returns: An exception if an exception occured
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    try:
        shutil.rmtree(notebook_path, ignore_errors=True)
    except OSError as exception:
        logging.info("Deleting a directory for a notebook ({})".format(nb_name))
        logging.exception(str(exception))

        return exception
