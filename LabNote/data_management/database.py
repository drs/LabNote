# Python import
import sqlite3
import os
import logging

# Project import
from LabNote.data_management import directory

MAIN_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/labnote.db")
PROTOCOL_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/protocols.db")

MAIN_DATABASE_VERSION = 2
PROTOCOL_DATABASE_VERSION = 1

SET_MAIN_DB_USER_VERSION = "PRAGMA user_version = '{}'".format(MAIN_DATABASE_VERSION)

CREATE_NOTEBOOK_TABLE = """
CREATE TABLE notebook (
    nb_id           INTEGER         PRIMARY KEY   AUTOINCREMENT,
    name            VARCHAR (255)   NOT NULL      UNIQUE, 
    uuid            CHAR (36)       UNIQUE        NOT NULL
)"""

CREATE_EXPERIMENT_TABLE = """
CREATE TABLE experiment (
    exp_id         INTEGER       PRIMARY KEY   AUTOINCREMENT,
    name           VARCHAR (255) NOT NULL      UNIQUE,
    objective      TEXT,
    uuid           CHAR (36)     NOT NULL      UNIQUE,
    nb_id           INTEGER       NOT NULL     REFERENCES notebook (nb_id)
)"""

CREATE_EXPERIMENT_INDEX = """
CREATE UNIQUE INDEX experiment_uuid ON experiment (
    uuid ASC
)"""

CREATE_DATASET_TABLE = """
CREATE TABLE dataset (
    data_id      INTEGER     PRIMARY KEY   AUTOINCREMENT,
    uuid         CHAR (36)   NOT NULL      UNIQUE,
    name         VARCHAR (255) 
)"""

CREATE_DATASET_INDEX = """
CREATE UNIQUE INDEX dataset_index ON dataset (
    uuid
)"""

CREATE_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    protocol_id     INTEGER   PRIMARY KEY   AUTOINCREMENT,
    uuid            CHAR (36) NOT NULL      UNIQUE,
    name            VARCHAR (255)
)
"""

CREATE_PROTOCOL_INDEX = """
CREATE UNIQUE INDEX protocol_index ON protocol (
    uuid
)"""

CREATE_EXPERIMENT_DATASET_TABLE = """
CREATE TABLE experiment_dataset (
    exp_id INTEGER REFERENCES experiment (exp_id)  NOT NULL,
    data_id    INTEGER REFERENCES dataset (data_id)       NOT NULL
)"""

CREATE_EXPERIMENT_DATASET_INDEX = """
CREATE UNIQUE INDEX experiment_dataset_index ON experiment_dataset (
    exp_id ASC,
    data_id ASC
)"""

CREATE_EXPERIMENT_PROTOCOL_TABLE = """
CREATE TABLE experiment_protocol (
    exp_id INTEGER REFERENCES experiment (exp_id)     NOT NULL,
    protocol_id   INTEGER REFERENCES protocol (protocol_id)         NOT NULL
)"""

CREATE_EXPERIMENT_PROTOCOL_INDEX = """
CREATE UNIQUE INDEX experiment_protocol_index ON experiment_protocol (
    exp_id ASC,
    protocol_id ASC
)"""

CREATE_PROTOCOL_DB_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    protocol_id       INTEGER       PRIMARY KEY AUTOINCREMENT,
    uuid              CHAR (36)     NOT NULL
                                    UNIQUE,
    name              VARCHAR (255) NOT NULL,
    research_field_id INTEGER       REFERENCES research_field (research_field_id),
    version           VARCHAR (16),
    revision          VARCHAR (16),
    body              TEXT,
    date_created      DATETIME      DEFAULT (CURRENT_TIMESTAMP),
    date_updated      DATETIME
)"""

CREATE_PROTOCOL_DB_INDEX = """
CREATE UNIQUE INDEX protocol_index ON protocol (
    uuid
)
"""

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
    research_field_id INTEGER           PRIMARY KEY     AUTOINCREMENT,
    name              VARCHAR (255)     NOT NULL        UNIQUE
)"""

SET_PROTOCOL_DB_USER_VERSION = "PRAGMA user_version = '{}'".format(PROTOCOL_DATABASE_VERSION)

SELECT_NOTEBOOK_NAME = """
SELECT uuid, name FROM notebook
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (name, uuid) VALUES ('{}', '{}')
"""

INSERT_EXPERIMENT = """
INSERT INTO experiment (name, uuid, objective, nb_id) VALUES ('{}', '{}', '{}', 
(SELECT nb_id FROM notebook WHERE notebook.uuid = '{}'))
"""

SELECT_NOTEBOOK_EXPERIMENT = """
SELECT name, objective, uuid FROM experiment WHERE nb_id = (SELECT nb_id FROM notebook WHERE notebook.uuid = '{}')
"""


def create_notebook(nb_name, nb_uuid):
    """ Create a new notebook

    :param nb_name: Name of the notebook to create
    :type nb_name: str
    :param nb_uuid: UUID of the notebook to create
    :type nb_uuid: UUID
    :returns: True if the notebook was created and false otherwise
    """

    conn = None
    query = INSERT_NOTEBOOK.format(nb_name, nb_uuid)

    try:
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as exception:
        # Log error
        logging.info("Creating a new notebook ({}) in the labnote.db".format(nb_name))
        logging.exception(str(exception))

        return exception
    finally:
        if conn:
            conn.close()


def get_notebook_list():
    """Get a list of all existing notebooks

    :return: List of dictionary of name and id of the notebooks
    """

    # Select notebook list from database
    buffer = None
    conn = None

    try:
        # Prepare the connection
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        cursor.execute(SELECT_NOTEBOOK_NAME)
        buffer = cursor.fetchall()
    except sqlite3.Error as exception:
        logging.info("Getting name and id of all notebooks from labnote.db")
        logging.exception(str(exception))

        return exception
    finally:
        if conn:
            conn.close()

    # Prepare the return format

    notebook_list = []

    for notebook in buffer:
        notebook_list.append({'uuid': notebook[0], 'name': notebook[1]})

    return notebook_list


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
        cursor.execute(CREATE_EXPERIMENT_INDEX)
        cursor.execute(CREATE_DATASET_TABLE)
        cursor.execute(CREATE_DATASET_INDEX)
        cursor.execute(CREATE_PROTOCOL_TABLE)
        cursor.execute(CREATE_PROTOCOL_INDEX)
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
        cursor.execute(CREATE_PROTOCOL_DB_INDEX)
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

    conn = None
    query = INSERT_EXPERIMENT.format(exp_name, exp_uuid, exp_obj, nb_uuid)

    try:
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as exception:
        # Log error
        logging.info("An exception occured while adding the experiment ({}) in the labnote.db".format(exp_uuid))
        logging.exception(str(exception))

        return exception
    finally:
        if conn:
            conn.close()


def get_experiment_list_notebook(nb_uuid):
    """ Get the experiment list for a specific notebook

    :param nb_uuid: UUID of the notebook
    :type nb_uuid: UUID
    :return: List of dictionary of name, objective and id of the notebooks
    """

    # Select notebook list from database
    buffer = None
    conn = None

    try:
        # Prepare the connection
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        query = SELECT_NOTEBOOK_EXPERIMENT.format(nb_uuid)

        cursor.execute(query)
        buffer = cursor.fetchall()
    except sqlite3.Error as exception:
        logging.info("An exception occured while getting a list all experiment for notebook {} "
                     "from labnote.db".format(nb_uuid))
        logging.exception(str(exception))

        return exception
    finally:
        if conn:
            conn.close()

    # Prepare the return format

    experiement_list = []

    for experiment in buffer:
        experiement_list.append({'uuid': experiment[2], 'name': experiment[0], 'objective': experiment[1]})

    return experiement_list
