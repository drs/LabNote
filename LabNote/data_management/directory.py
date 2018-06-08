# Python import
import os
import logging
import shutil

# PyQt import
from PyQt5.QtWidgets import QMessageBox

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


def create_default_main_directory(silent=False):
    """ Create the main directory at it's default location

    :param silent: Hide the messagebox if true
    :type silent: bool
    """

    # Create the defaults directories
    try:
        os.mkdir(DEFAULT_MAIN_DIRECTORY_PATH)
        os.mkdir(os.path.join(NOTEBOOK_DIRECTORY_PATH))
        os.mkdir(logs.LOG_DIRECTORY_PATH)
    except OSError as exception:
        # Warn the user about the error
        # This is a fatal error as the program cannot continue without a basic file structure
        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("File structure cannot be created")
            message.setInformativeText("The file structure required to save the user information cannot be created."
                                   "The program will now close. Please delete any LabNote directory in Documents as"
                                   "it might interfere with a new program installation.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Try to cleanup the main directory
        try:
            cleanup_main_directory()
        except:
            raise # Raise any possible exception that can happen at this point

        raise


def create_nb_directory(nb_name, nb_uuid, silent=False):
    """ Create a directory for a new notebook

    :param nb_name: Notebook name
    :type nb_name: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :param silent: If true the messagebox are not shown
    :type silent: bool
    :returns: True if the directory is created and false otherwise
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    try:
        os.mkdir(notebook_path)
    except OSError as e:
        #  Log the exception
        logging.info("Creating a directory for a notebook ({})".format(nb_name))
        logging.exception(str(e))

        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Notebook cannot be created")
            message.setInformativeText("An error occurred during the notebook directory creation.")
            message.setDetailedText(str(e))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        return False
    return True


def delete_nb_directory(nb_name, nb_uuid, silent=False):
    """ Delete a notebook directory

    :param nb_name: Notebook name
    :type nb_name: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :param silent: Hide the messagebox if true
    :type silent: bool
    :returns: True if the directory is created and false otherwise
    """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    try:
        shutil.rmtree(notebook_path, ignore_errors=True)
    except OSError as e:
        logging.info("Deleting a directory for a notebook ({})".format(nb_name))
        logging.exception(str(e))

        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Notebook cannot be deleted")
            message.setInformativeText("An error occurred during the notebook directory deletion. The notebook with UUID {}"
                                   " should be deleted manually.".format(nb_uuid))
            message.setDetailedText(str(e))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        return False
    return True
