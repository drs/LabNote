""" This module is responsible of the file system entry operations which include directory and database operations
for every kind of entry. """

# Python import
import shutil
import uuid
import os

# Projet import
from labnote.utils import database, directory, files


def check_integrity():
    """ Create the main directory if it does not exist """
    if not os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH):
        create_main_directory()


def create_main_directory():
    """ Create the main directory """
    directory.create_default_main_directory()
    database.create_main_database()


def cleanup_main_directory():
    """ Delete the main directory """
    shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)


def create_notebook(nb_name, proj_id):
    """ Create a notebook

    :param nb_name: Notebook name
    :type nb_name: str
    :param proj_id: Project ID for the notebook
    :type proj_id: int
    """

    # Create UUID
    nb_uuid = str(uuid.uuid4())
    directory.create_nb_directory(nb_uuid)
    database.create_notebook(nb_name, nb_uuid, proj_id)


def add_reference_pdf(ref_uuid, file):
    """ Add a reference PDF in the file structure and the database

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    :param file: Orignal file path
    :type file: str
    """
    database.update_reference_file(ref_uuid=ref_uuid, file_attached=True)
    files.copy_reference(ref_uuid=ref_uuid, file=file)


def delete_reference_file(ref_uuid):
    """ Delete a reference PDF in the file structure and the database

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    """
    database.update_reference_file(ref_uuid=ref_uuid, file_attached=False)
    files.delete_reference(ref_uuid=ref_uuid)
