# Python import
import sqlite3
import os
import collections

# Project import
from LabNote.data_management import directory

MAIN_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/labnote.db")
PROTOCOL_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/protocols.db")

MAIN_DATABASE_VERSION = 2
PROTOCOL_DATABASE_VERSION = 1

SET_MAIN_DB_USER_VERSION = "PRAGMA user_version = '{}'".format(MAIN_DATABASE_VERSION)

CREATE_NOTEBOOK_TABLE = """
CREATE TABLE notebook (
    nb_uuid     BLOB (16)         PRIMARY KEY,
    nb_name     VARCHAR (255)     NOT NULL          UNIQUE
)"""

CREATE_EXPERIMENT_TABLE = """
CREATE TABLE experiment (
    exp_uuid      BLOB (16)     PRIMARY KEY,
    exp_name      VARCHAR (255) NOT NULL,
    nb_uuid       BLOB          REFERENCES notebook (nb_uuid)     ON DELETE CASCADE     NOT NULL,
    exp_objective TEXT
)"""

CREATE_DATASET_TABLE = """
CREATE TABLE dataset (
    dataset_uuid    BLOB (16)         PRIMARY KEY,
    dataset_name    VARCHAR (255) 
)"""

CREATE_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    protocol_uuid     BLOB (16)         PRIMARY KEY,
    protocol_name     VARCHAR (255) 
)"""

CREATE_EXPERIMENT_DATASET_TABLE = """
CREATE TABLE experiment_dataset (
    exp_uuid      BLOB (16)    REFERENCES experiment (exp_uuid)       ON DELETE CASCADE     NOT NULL,
    dataset_uuid  BLOB (16)    REFERENCES dataset (dataset_uuid)      ON DELETE RESTRICT    NOT NULL
)"""

CREATE_EXPERIMENT_DATASET_INDEX = """
CREATE UNIQUE INDEX experiment_dataset_index ON experiment_dataset (
    exp_uuid        ASC,
    dataset_uuid    ASC
)"""

CREATE_EXPERIMENT_PROTOCOL_TABLE = """
CREATE TABLE experiment_protocol (
    exp_uuid        BLOB (16)     REFERENCES experiment (exp_uuid)      ON DELETE CASCADE       NOT NULL,
    protocol_uuid   BLOB (16)     REFERENCES protocol (protocol_uuid)   ON DELETE RESTRICT      NOT NULL
)"""

CREATE_EXPERIMENT_PROTOCOL_INDEX = """
CREATE UNIQUE INDEX experiment_protocol_index ON experiment_protocol (
    exp_uuid ASC,
    protocol_uuid ASC
)"""

CREATE_PROTOCOL_DB_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    protocol_uuid     BLOB (16)     PRIMARY KEY,
    name              VARCHAR (255) NOT NULL,
    research_field_id INTEGER       REFERENCES research_field (research_field_id),
    version           VARCHAR (16),
    revision          VARCHAR (16),
    body              TEXT,
    date_created      DATETIME      DEFAULT (CURRENT_TIMESTAMP),
    date_updated      DATETIME
)"""

CREATE_PROTOCOL_DB_UPDATE_DATE_TRIGGER = """
CREATE TRIGGER update_date
         AFTER UPDATE OF body
            ON protocol
BEGIN
    UPDATE protocol
       SET date_updated = CURRENT_TIMESTAMP;
END"""

CREATE_PROTOCOL_DB_RESEACH_FIELD_TABLE = """
CREATE TABLE research_field (
    research_field_id INTEGER       PRIMARY KEY AUTOINCREMENT,
    name              VARCHAR (255) NOT NULL      UNIQUE
)"""

SET_PROTOCOL_DB_USER_VERSION = "PRAGMA user_version = '{}'".format(PROTOCOL_DATABASE_VERSION)

SELECT_NOTEBOOK_NAME = """
SELECT nb_uuid, nb_name FROM notebook
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (nb_uuid, nb_name) VALUES ('{}', '{}')
"""

INSERT_EXPERIMENT = """
INSERT INTO experiment (exp_uuid, nb_uuid, exp_name, exp_objective) VALUES ('{}', '{}', '{}', '{}')
"""

SELECT_NOTEBOOK_EXPERIMENT = """
SELECT exp_uuid, exp_name, exp_objective FROM experiment WHERE nb_uuid =  '{}'
"""

UPDATE_NOTEBOOK_NAME = """
UPDATE notebook SET nb_name = '{}' WHERE nb_uuid = '{}'
"""

DELETE_NOTEBOOK = """
DELETE FROM notebook WHERE nb_uuid = '{}'
"""

SELECT_EXPERIMENT = """
SELECT exp_name, exp_objective FROM experiment WHERE exp_uuid = '{}'
"""

# Named tuples Returns
# Should be used when a function can return either an error or a list
Returns = collections.namedtuple('Returns', ['lst', 'error'])
Returns.__new__.__defaults__ = ([], None)


def execute_query(query):
    """ Execute the query

    :param query: Query to execute
    :type query: str
    :returns: An sqlite3.Error is an exception occured
    """

    conn = None

    try:
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as exception:
        return exception
    finally:
        if conn:
            conn.close()


def create_notebook(nb_name, nb_uuid):
    """ Create a new notebook

    :param nb_name: Name of the notebook to create
    :type nb_name: str
    :param nb_uuid: UUID of the notebook to create
    :type nb_uuid: UUID
    :returns: An sqlite3.Error is an exception occured
    """
    query = INSERT_NOTEBOOK.format(nb_uuid, nb_name)
    return execute_query(query)


def update_notebook_name(new_name, nb_uuid):
    """ Update the name of a notebook

    :param new_name: New name for the notebook
    :type new_name: str
    :param nb_uuid: UUID of the notebook to rename
    :type nb_uuid: UUID
    :returns: An sqlite3.Error is an exception occured
    """
    query = UPDATE_NOTEBOOK_NAME.format(new_name, nb_uuid)
    return execute_query(query)


def delete_notebook(nb_uuid):
    """ Delete a notebook from the database

    :param nb_uuid: UUID of the notebook to delete
    :type nb_uuid: UUID
    :returns: An sqlite3.Error is an exception occured
    """
    query = DELETE_NOTEBOOK.format(nb_uuid)
    return execute_query(query)


def get_notebook_list():
    """Get a list of all existing notebooks

    :return: List of dictionary of name and id of the notebooks
    """

    # Select notebook list from database
    conn = None

    try:
        # Prepare the connection
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        cursor.execute(SELECT_NOTEBOOK_NAME)
        buffer = cursor.fetchall()
    except sqlite3.Error as exception:
        return Returns(error=exception)
    finally:
        if conn:
            conn.close()

    # Prepare the return format

    notebook_list = []

    for notebook in buffer:
        notebook_list.append({'uuid': notebook[0], 'name': notebook[1]})

    return Returns(lst=notebook_list)


def create_main_database():
    """ Create the labnote database """

    conn = None

    try:
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        conn.isolation_level = None
        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(SET_MAIN_DB_USER_VERSION)
        cursor.execute(CREATE_NOTEBOOK_TABLE)
        cursor.execute(CREATE_EXPERIMENT_TABLE)
        cursor.execute(CREATE_DATASET_TABLE)
        cursor.execute(CREATE_PROTOCOL_TABLE)
        cursor.execute(CREATE_EXPERIMENT_DATASET_TABLE)
        cursor.execute(CREATE_EXPERIMENT_DATASET_INDEX)
        cursor.execute(CREATE_EXPERIMENT_PROTOCOL_TABLE)
        cursor.execute(CREATE_EXPERIMENT_PROTOCOL_INDEX)
        cursor.execute("COMMIT")
    except sqlite3.Error as exception:
        # Try to cleanup the main directory
        try:
            directory.cleanup_main_directory()
        except:
            pass  # No need to raise any exception as an error message is already shown to the user

        return exception
    finally:
        if conn:
            conn.close()


def create_protocol_db():
    """ Create the protocole database """

    conn = None

    try:
        conn = sqlite3.connect(PROTOCOL_DATABASE_FILE_PATH)
        conn.isolation_level = None

        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(SET_PROTOCOL_DB_USER_VERSION)
        cursor.execute(CREATE_PROTOCOL_DB_RESEACH_FIELD_TABLE)
        cursor.execute(CREATE_PROTOCOL_DB_PROTOCOL_TABLE)
        cursor.execute(CREATE_PROTOCOL_DB_UPDATE_DATE_TRIGGER)
        cursor.execute("COMMIT")
    except sqlite3.Error as exception:
        # Try to cleanup the main directory
        try:
            directory.cleanup_main_directory()
        except:
            pass  # No need to raise any exception as an error message is already shown to the user

        return exception
    finally:
        if conn:
            conn.close()


def create_experiment(exp_name, exp_uuid, exp_obj, nb_uuid):
    """ Create a new experiment in the main database """
    query = INSERT_EXPERIMENT.format(exp_uuid, nb_uuid, exp_name, exp_obj)
    return execute_query(query)


def get_experiment_list_notebook(nb_uuid):
    """ Get the experiment list for a specific notebook

    :param nb_uuid: UUID of the notebook
    :type nb_uuid: UUID
    :returns: List of dictionary of name, objective and id of the notebooks
    """

    # Select notebook list from database
    conn = None

    try:
        # Prepare the connection
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        query = SELECT_NOTEBOOK_EXPERIMENT.format(nb_uuid)

        cursor.execute(query)
        buffer = cursor.fetchall()
    except sqlite3.Error as exception:
        return Returns(error=exception)
    finally:
        if conn:
            conn.close()

    # Prepare the return format

    experiement_list = []

    for experiment in buffer:
        experiement_list.append({'uuid': experiment[0], 'name': experiment[1], 'objective': experiment[2]})

    return Returns(lst=experiement_list)


def get_experiment_informations(exp_uuid):
    """ Get informations for an experiment

    :param exp_uuid: Experiment UUID
    :type exp_uuid: UUID
    :returns: Dictionary with the name, objective of the notebook
    """
    conn = None

    try:
        # Select the experiment from the database
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        query = SELECT_EXPERIMENT.format(exp_uuid)

        cursor.execute(query)
        buffer = cursor.fetchall()
    except sqlite3.Error as exception:
        return Returns(error=exception)
    finally:
        if conn:
            conn.close()

    # Return experiment informations
    return Returns(lst=[{'name': buffer[0], 'objective': buffer[1]}])