# Python import
import os
import logging
import sys

# PyQt import
from PyQt5.QtWidgets import QMessageBox

# Project import
from common import logs

DEFAULT_MAIN_DIRECTORY_PATH = logs.DEFAULT_MAIN_DIRECTORY_PATH # This is required to avoid double dependancy
NOTEBOOK_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/notebook")


def create_default_main_directory():
    """ Create the main directory at it's default location """

    # Create the defaults directories
    try:
        os.mkdir(DEFAULT_MAIN_DIRECTORY_PATH)
        os.mkdir(os.path.join(NOTEBOOK_DIRECTORY_PATH))
        os.mkdir(logs.LOG_FILE_PATH)
    except OSError as e:
        # Warn the user about the error
        # This is a fatal error as the program cannot continue without a basic file structure
        message = QMessageBox()
        message.setWindowTitle("LabNote")
        message.setText("File structure cannot be created")
        message.setInformativeText("The file structure required to save the user information cannot be created."
                                   "The program cannot be started.")
        message.setDetailedText(str(e))
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec()

        # Exit the program
        sys.exit()


def create_nb_directory(nb_name, nb_uuid):
    """ Create a directory for a new notebook """
    notebook_path = os.path.join(NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))

    try:
        os.mkdir(notebook_path)
    except OSError as e:
        logging.info("Creating a directory for a notebook ({})".format(nb_name))
        logging.exception(str(e))
        raise
