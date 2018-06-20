""" This module is responsible of the file system entry operations which include directory and database operations
for every kind of entry. """

# Python import
import shutil
import uuid

# Projet import
from labnote.utils import database, directory


def create_main_directory():
    """ Create the main directory """
    directory.create_default_main_directory()
    database.create_main_database()
    database.create_protocol_db()


def cleanup_main_directory():
    """ Delete the main directory """
    shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)


def create_notebook(nb_name):
    """ Create a notebook

    :param nb_name: Notebook name
    :type nb_name: str
    """

    # Create UUID
    nb_uuid = str(uuid.uuid4())
    directory.create_nb_directory(nb_uuid)
    database.create_notebook(nb_name, nb_uuid)
