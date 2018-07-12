""" This module is responsible of the file system entry operations which include directory and database operations
for every kind of entry. """

# Python import
import shutil
import uuid
import os
import sqlite3

# Projet import
from labnote.utils import database, directory, files
from labnote.core import data


def check_main_directory():
    """ Create the main directory if it does not exist """
    if not os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH):
        create_main_directory()


def create_main_directory():
    """ Create the main directory """
    os.mkdir(directory.DEFAULT_MAIN_DIRECTORY_PATH)
    os.mkdir(directory.NOTEBOOK_DIRECTORY_PATH)
    os.mkdir(directory.REFERENCES_DIRECTORY_PATH)
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

    conn = None
    exception = False

    # Create UUID
    nb_uuid = str(uuid.uuid4())

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(database.INSERT_NOTEBOOK, {'nb_uuid': data.uuid_bytes(nb_uuid), 'name': nb_name,
                                                  'proj_id': proj_id})

        notebook_path = directory.notebook_path(nb_uuid=nb_uuid)
        os.mkdir(notebook_path)
        dataset_path = directory.dataset_notebook_path(nb_uuid=nb_uuid)
        os.mkdir(dataset_path)
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            conn.rollback()
        exception = True
        raise
    finally:
        if not exception:
            if conn:
                conn.commit()
        if conn:
            conn.close()


def delete_notebook(nb_uuid):
    """ Delete a notebook from the database and the file structure

    :param nb_uuid: Notebook UUID
    :type str:
    """
    conn = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(database.DELETE_NOTEBOOK, {'nb_uuid': data.uuid_bytes(nb_uuid)})

        notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
        shutil.rmtree(notebook_path, ignore_errors=True)
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            conn.rollback()
        exception = True
        raise
    finally:
        if not exception:
            conn.commit()
        if conn:
            conn.close()


def add_reference_pdf(ref_uuid, file):
    """ Add a reference PDF in the file structure and the database

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    :param file: Orignal file path
    :type file: str
    """
    conn = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute(database.UPDATE_REFERENCE_FILE, {'file_attached': True, 'ref_uuid': data.uuid_bytes(ref_uuid)})

        reference_file = files.reference_file_path(ref_uuid=ref_uuid)
        shutil.copy2(file, reference_file)
        return reference_file
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            conn.rollback()
        exception = True
        raise
    finally:
        if not exception:
            if conn:
                conn.commit()
        if conn:
            conn.close()


def delete_reference_pdf(ref_uuid):
    """ Delete a reference PDF in the file structure and the database

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    """
    conn = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute(database.UPDATE_REFERENCE_FILE, {'file_attached': False, 'ref_uuid': data.uuid_bytes(ref_uuid)})

        reference_file = files.reference_file_path(ref_uuid=ref_uuid)
        os.remove(reference_file)
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            conn.rollback()
        exception = True
        raise
    finally:
        if not exception:
            conn.commit()
        if conn:
            conn.close()


def create_dataset(dt_uuid, name, key, nb_uuid):
    """ Create a dataset in the database and in the file structure

    :param dt_uuid: Dataset uuid
    :type dt_uuid: str
    :param name: Dataset name
    :type name: str
    :param key: Dataset key
    :type key: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    """

    conn = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(database.INSERT_DATASET, {'dt_uuid': data.uuid_bytes(dt_uuid), 'name': name, 'dt_key': key,
                                                 'nb_uuid': data.uuid_bytes(nb_uuid)})

        dataset_folder = directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid)
        os.mkdir(dataset_folder)
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            conn.rollback()
        exception = True
        raise
    finally:
        if not exception:
            conn.commit()
        if conn:
            conn.close()


def delete_dataset(dt_uuid, nb_uuid):
    """ Delete a dataset from the database and the file structure

    :param dt_uuid: Dataset uuid
    :type dt_uuid: str
    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    """

    conn = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(database.DELETE_DATASET, {'dt_uuid': data.uuid_bytes(dt_uuid)})

        dataset_folder = directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid)
        shutil.rmtree(dataset_folder, ignore_errors=True)
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            conn.rollback()
        exception = True
        raise
    finally:
        if not exception:
            conn.commit()
        if conn:
            conn.close()
