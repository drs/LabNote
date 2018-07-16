""" This module is responsible of the file system entry operations which include directory and database operations
for every kind of entry. """

# Python import
import shutil
import uuid
import os
import sqlite3

# Projet import
from labnote.utils import database, directory, files
from labnote.core import data, sqlite_error


"""
General entry
"""


def check_main_directory():
    """ Create the main directory if it does not exist """
    if not os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH):
        create_main_directory()


def create_main_directory():
    """ Create the main directory """
    os.mkdir(directory.DEFAULT_MAIN_DIRECTORY_PATH)
    os.mkdir(directory.NOTEBOOK_DIRECTORY_PATH)
    os.mkdir(directory.REFERENCES_DIRECTORY_PATH)
    os.mkdir(directory.PROTOCOL_DIRECTORY_PATH)
    database.create_main_database()


def cleanup_main_directory():
    """ Delete the main directory """
    shutil.rmtree(directory.DEFAULT_MAIN_DIRECTORY_PATH, ignore_errors=True)


""" 
Notebook entry
"""


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


"""
Reference entry
"""


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


def delete_reference(ref_uuid):
    """ Delete a reference from the database and cleanup any PDF file from the file system
    or tag in the database """

    conn = None
    cursor = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN ")
        cursor.execute(database.SELECT_REFERENCE_TAG, {'ref_uuid': data.uuid_bytes(ref_uuid)})
        tag_ids = cursor.fetchall()
        cursor.execute(database.DELETE_REF, {'ref_uuid': data.uuid_bytes(ref_uuid)})

        if tag_ids:
            try:
                for tag_id in tag_ids[0]:
                    cursor.execute(database.DELETE_TAG_ID, {'tag_id': tag_id})
            except sqlite3.Error as excpt:
                if sqlite_error.sqlite_err_handler(str(excpt)) == sqlite_error.FOREIGN_KEY_CODE:
                    pass
                else:
                    raise

        reference_file = files.reference_file_path(ref_uuid=ref_uuid)
    except sqlite3.Error:
        exception = True
        raise
    except FileNotFoundError:
        pass
    except OSError:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK")
        exception = True
        raise
    finally:
        if not exception:
            if cursor:
                cursor.execute("END")
        if conn:
            conn.close()


"""
Dataset entry
"""


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


"""
Protocol entry
"""


def create_protocol(prt_uuid, prt_key, category_id, body, tag_list, reference_list,
                    description=None, name=None, subcategory_id=None):
    """ Create a protocol in the database and the file system

    :param prt_uuid: Protocol UUID
    :type prt_uuid: str
    :param prt_key: Protocol key
    :type prt_key: str
    :param name: Protocol name
    :type name: str
    """

    conn = None
    cursor = None
    file = None
    exception = False

    try:
        # Add protocol in the database
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        cursor.execute(database.INSERT_PROTOCOL, {'prt_uuid': data.uuid_bytes(prt_uuid),
                                                  'prt_key': prt_key,
                                                  'name': name,
                                                  'description': description,
                                                  'category_id': category_id,
                                                  'subcategory_id': subcategory_id})

        if tag_list:
            for tag in tag_list:
                cursor.execute(database.INSERT_TAG, {'name': tag})
                cursor.execute(database.INSERT_TAG_PROTOCOL, {'prot_uuid': data.uuid_bytes(prt_uuid), 'name': tag})

        if reference_list:
            for reference in reference_list:
                cursor.execute(database.INSERT_REF_PROTOCOL, {'prot_uuid': data.uuid_bytes(prt_uuid),
                                                              'ref_uuid': data.uuid_bytes(reference)})

        # Create the file directory
        protocol_path = directory.protocol_path(prt_uuid=prt_uuid)
        protocol_resource_path = directory.protocol_resource_path(prt_uuid=prt_uuid)
        os.mkdir(protocol_path)
        os.mkdir(protocol_resource_path)

        # Create the protocol body file
        file = open(files.protocol_file(prt_uuid), 'wb')
        file.write(data.encode(body))
    except sqlite3.Error:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    except OSError:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    finally:
        if not exception:
            if cursor:
                cursor.execute("COMMIT")
        if conn:
            conn.close()
        if file:
            file.close()


def save_protocol(prt_uuid, prt_key, name, description, body, tag_list, reference_list, deleted_image):
    """ Save changes to a protocol in the database and the file system """

    conn = None
    file = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        cursor.execute(database.UPDATE_PROTOCOL, {'prt_uuid': data.uuid_bytes(prt_uuid),
                                                  'prt_key': prt_key,
                                                  'name': name,
                                                  'description': description})

        uuid_dict = {'prot_uuid': data.uuid_bytes(prt_uuid)}

        # Handle the tags
        cursor.execute(database.SELECT_PROTOCOL_TAG_NAME, uuid_dict)
        current_tag_list = cursor.fetchall()
        cursor.execute(database.SELECT_PROTOCOL_REFERENCE_UUID, uuid_dict)
        current_reference_list = cursor.fetchall()

        database.process_tag(cursor=cursor, insert_list=tag_list, current_list=current_tag_list,
                             insert=database.INSERT_TAG_PROTOCOL, delete=database.DELETE_TAG_PROTOCOL,
                             value=uuid_dict)
        database.process_key(cursor=cursor, insert_list=reference_list, current_list=current_reference_list,
                             insert=database.INSERT_REF_PROTOCOL, delete=database.DELETE_REF_PROTOCOL,
                             value=uuid_dict, key='ref_uuid')

        # Save the text file
        file = open(files.protocol_file(prt_uuid), 'wb')
        file.write(data.encode(body))

        # Remove deleted image
        if deleted_image:
            for path in deleted_image:
                os.remove(path)
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
        if file:
            file.close()


def delete_protocol(prt_uuid):
    """ Delete a protocol from the database and the file structure

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    """

    conn = None
    cursor = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN")

        cursor.execute(database.SELECT_PROTOCOL_TAG, {'prot_uuid': data.uuid_bytes(prt_uuid)})
        tag_ids = cursor.fetchall()

        cursor.execute(database.DELETE_PROTOCOL, {'prt_uuid': data.uuid_bytes(prt_uuid)})

        if tag_ids:
            try:
                for tag_id in tag_ids[0]:
                    cursor.execute(database.DELETE_TAG_ID, {'tag_id': tag_id})
            except sqlite3.Error as excpt:
                if sqlite_error.sqlite_err_handler(str(excpt)) == sqlite_error.FOREIGN_KEY_CODE:
                    pass
                else:
                    raise

        protocol_path = directory.protocol_path(prt_uuid=prt_uuid)
        shutil.rmtree(protocol_path, ignore_errors=True)
    except sqlite3.Error:
        exception = True
        raise
    except OSError:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK")
        exception = True
        raise
    finally:
        if not exception:
            if cursor:
                cursor.execute("COMMIT")
        if conn:
            conn.close()


def read_protocol(prt_uuid):
    """ Read a protocol content from the database and the file system

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return {}: Protocol content
    """

    buffer = None
    body_buffer = None

    try:
        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(database.SELECT_PROTOCOL, {'prt_uuid': data.uuid_bytes(prt_uuid)})
            buffer = cursor.fetchall()[0]

        with open(files.protocol_file(prt_uuid), 'rb') as file:
            body_buffer = data.decode(file.read())
    except (sqlite3.Error, OSError):
        raise

    protocol = {'key': buffer[0], 'name': buffer[1], 'description': buffer[2], 'created': buffer[3],
                'updated': buffer[4], 'body': body_buffer}
    return protocol


"""
Experiment entry
"""


def create_experiment(exp_uuid, nb_uuid, name, exp_key=None, description=None, body=None, tag_list=None,
                      reference_list=None, dataset_list=None, protocol_list=None):
    """ Create a protocol in the database and the file system

    :param prt_uuid: Protocol UUID
    :type prt_uuid: str
    :param prt_key: Protocol key
    :type prt_key: str
    :param name: Protocol name
    :type name: str
    """

    conn = None
    cursor = None
    file = None
    exception = False

    try:
        # Add protocol in the database
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        cursor.execute(database.INSERT_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid),
                                                    'exp_key': exp_key,
                                                    'name': name,
                                                    'description': description,
                                                    'nb_uuid': data.uuid_bytes(nb_uuid)})

        if tag_list:
            for tag in tag_list:
                cursor.execute(database.INSERT_TAG, {'name': tag})
                cursor.execute(database.INSERT_TAG_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid),
                                                                'name': tag})

        if reference_list:
            for reference in reference_list:
                cursor.execute(database.INSERT_REF_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid),
                                                                'ref_uuid': data.uuid_bytes(reference)})

        if dataset_list:
            for dataset in dataset_list:
                cursor.execute(database.INSERT_DATASET_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid),
                                                                    'dt_uuid': data.uuid_bytes(dataset)})

        if protocol_list:
            for protocol in protocol_list:
                cursor.execute(database.INSERT_PROTOCOL_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid),
                                                                     'prt_uuid': data.uuid_bytes(protocol)})


        # Create the file directory
        experiment_path = directory.experiment_path(nb_uuid, exp_uuid)
        experiment_resource_path = directory.experiment_resource_path(nb_uuid, exp_uuid)
        os.mkdir(experiment_path)
        os.mkdir(experiment_resource_path)

        # Create the protocol body file
        file = open(files.experiment_file(nb_uuid, exp_uuid), 'wb')
        file.write(data.encode(body))
    except sqlite3.Error:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    except OSError:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    finally:
        if not exception:
            if cursor:
                cursor.execute("COMMIT")
        if conn:
            conn.close()
        if file:
            file.close()


def save_experiment(exp_uuid, nb_uuid, name, exp_key, description, body, tag_list, reference_list, dataset_list,
                    protocol_list, deleted_image):
    """ Save changes to an experiment in the database and the file system """

    conn = None
    cursor = None
    file = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        cursor.execute(database.UPDATE_EXPERIMENT, {'exp_key': exp_key,
                                                    'name': name,
                                                    'description': description,
                                                    'exp_uuid': data.uuid_bytes(exp_uuid)})

        uuid_dict = {'exp_uuid': data.uuid_bytes(exp_uuid)}

        # Handle the tags
        cursor.execute(database.SELECT_EXPERIMENT_TAG_NAME, uuid_dict)
        current_tag_list = cursor.fetchall()
        cursor.execute(database.SELECT_EXPERIMENT_REFERENCE_UUID, uuid_dict)
        current_reference_list = cursor.fetchall()
        cursor.execute(database.SELECT_EXPERIMENT_DATASET_UUID, uuid_dict)
        current_dataset_list = cursor.fetchall()
        cursor.execute(database.SELECT_EXPERIMENT_PROTOCOL_UUID,  uuid_dict)
        current_protocol_list = cursor.fetchall()

        database.process_tag(cursor=cursor, insert_list=tag_list, current_list=current_tag_list,
                             insert=database.INSERT_TAG_EXPERIMENT, delete=database.DELETE_TAG_EXPERIMENT,
                             value=uuid_dict)
        database.process_key(cursor=cursor, insert_list=reference_list, current_list=current_reference_list,
                             insert=database.INSERT_REF_EXPERIMENT, delete=database.DELETE_REF_EXPERIMENT,
                             value=uuid_dict, key='ref_uuid')
        database.process_key(cursor=cursor, insert_list=dataset_list, current_list=current_dataset_list,
                             insert=database.INSERT_DATASET_EXPERIMENT, delete=database.DELETE_DATASET_EXPERIMENT,
                             value=uuid_dict, key='dt_uuid')
        database.process_key(cursor=cursor, insert_list=protocol_list, current_list=current_protocol_list,
                             insert=database.INSERT_PROTOCOL_EXPERIMENT, delete=database.DELETE_PROTOCOL_EXPERIMENT,
                             value=uuid_dict, key='prt_uuid')

        # Create the protocol body file
        file = open(files.experiment_file(nb_uuid, exp_uuid), 'wb')
        file.write(data.encode(body))

        # Remove deleted image
        if deleted_image:
            for path in deleted_image:
                os.remove(path)
    except sqlite3.Error:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    except OSError:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    finally:
        if not exception:
            if cursor:
                cursor.execute("COMMIT")
        if conn:
            conn.close()
        if file:
            file.close()


def delete_experiment(nb_uuid, exp_uuid):
    """ Delete an experiment from the database and the file structure

    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    """

    conn = None
    cursor = None
    exception = False

    try:
        conn = sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("BEGIN")

        cursor.execute(database.SELECT_EXPERIMENT_TAG, {'exp_uuid': data.uuid_bytes(exp_uuid)})
        tag_ids = cursor.fetchall()

        cursor.execute(database.DELETE_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid)})

        if tag_ids:
            try:
                for tag_id in tag_ids[0]:
                    cursor.execute(database.DELETE_TAG_ID, {'tag_id': tag_id})
            except sqlite3.Error as excpt:
                if sqlite_error.sqlite_err_handler(str(excpt)) == sqlite_error.FOREIGN_KEY_CODE:
                    pass
                else:
                    raise

        experiment_path = directory.experiment_path(nb_uuid=nb_uuid, exp_uuid=exp_uuid)
        shutil.rmtree(experiment_path, ignore_errors=True)
    except sqlite3.Error:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK ")
        exception = True
        raise
    except OSError:
        if conn:
            if cursor:
                cursor.execute("ROLLBACK")
        exception = True
        raise
    finally:
        if not exception:
            if cursor:
                cursor.execute("COMMIT")
        if conn:
            conn.close()


def read_experiment(nb_uuid, exp_uuid):
    """ Read a protocol content from the database and the file system

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return {}: Protocol content
    """

    try:
        with sqlite3.connect(database.MAIN_DATABASE_FILE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(database.SELECT_EXPERIMENT, {'exp_uuid': data.uuid_bytes(exp_uuid)})
            buffer = cursor.fetchall()[0]

        with open(files.experiment_file(nb_uuid=nb_uuid, exp_uuid=exp_uuid), 'rb') as file:
            body_buffer = data.decode(file.read())
    except (sqlite3.Error, OSError):
        raise

    protocol = {'key': buffer[0], 'name': buffer[1], 'description': buffer[2], 'created': buffer[3],
                'updated': buffer[4], 'body': body_buffer}
    return protocol
