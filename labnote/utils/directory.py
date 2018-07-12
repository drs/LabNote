# Python import
import os
import shutil

DEFAULT_MAIN_DIRECTORY_PATH = os.path.expanduser("~/Documents/LabNote")
NOTEBOOK_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/Notebook")
REFERENCES_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/References")


def create_default_main_directory():
    """ Create the main directory at it's default location """

    # Create the defaults directories
    os.mkdir(DEFAULT_MAIN_DIRECTORY_PATH)
    os.mkdir(NOTEBOOK_DIRECTORY_PATH)
    os.mkdir(REFERENCES_DIRECTORY_PATH)