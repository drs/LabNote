# Python import
import sqlite3
import os
import uuid

# Project import
from labnote.utils import directory
from labnote.utils.conversion import uuid_bytes, uuid_string

"""
Database path
"""

MAIN_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/labnote.db")
PROTOCOL_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/protocols.db")

"""
Database version
"""

MAIN_DATABASE_VERSION = 3
PROTOCOL_DATABASE_VERSION = 2

"""
Database query
"""

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

SELECT_NOTEBOOK = """
SELECT nb_uuid, nb_name FROM notebook ORDER BY nb_name ASC
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (nb_uuid, nb_name) VALUES (:nb_uuid, :nb_name)
"""

INSERT_EXPERIMENT = """
INSERT INTO experiment (exp_uuid, nb_uuid, exp_name, exp_objective) 
VALUES (:exp_uuid, :nb_uuid, :exp_name, :exp_objective)
"""

SELECT_NOTEBOOK_EXPERIMENT = """
SELECT exp_uuid, exp_name, exp_objective FROM experiment WHERE nb_uuid = :nb_uuid
"""

UPDATE_NOTEBOOK_NAME = """
UPDATE notebook SET nb_name = :nb_name WHERE nb_uuid = :nb_uuid
"""

DELETE_NOTEBOOK = """
DELETE FROM notebook WHERE nb_uuid = :nb_uuid
"""

SELECT_EXPERIMENT = """
SELECT exp_name, exp_objective FROM experiment WHERE exp_uuid = :exp_uuid
"""

UPDATE_EXPERIMENT = """
UPDATE experiment SET exp_name = :exp_name, exp_objective = :exp_objective WHERE  exp_uuid = :exp_uuid
"""

DELETE_EXPERIMENT = """
DELETE FROM experiment WHERE exp_uuid = :exp_uuid
"""

"""
Database creation
"""


def create_main_database():
    """ Create the labnote database """

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
    conn.close()


def create_protocol_db():
    """ Create the protocole database """

    conn = sqlite3.connect(PROTOCOL_DATABASE_FILE_PATH)
    conn.isolation_level = None

    cursor = conn.cursor()

    cursor.execute("BEGIN")
    cursor.execute(SET_PROTOCOL_DB_USER_VERSION)
    cursor.execute(CREATE_PROTOCOL_DB_RESEACH_FIELD_TABLE)
    cursor.execute(CREATE_PROTOCOL_DB_PROTOCOL_TABLE)
    cursor.execute(CREATE_PROTOCOL_DB_UPDATE_DATE_TRIGGER)
    cursor.execute("COMMIT")
    conn.close()


"""
Generic query function
"""


def execute_query(query, **kwargs):
    """ Execute an sqlite query to the main database that does not return anything

    :param query: sqlite3 query
    :type query: str
    :param kwargs: query named placeholder content
    :returns: cursor.fetchall result
    """
    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, kwargs)
    buffer = cursor.fetchall()
    conn.commit()
    conn.close()

    return buffer


"""
Notebook table query
"""


def create_notebook(nb_name, nb_uuid):
    """ Create a new notebook

    :param nb_name: Name of the notebook to create
    :type nb_name: str
    :param nb_uuid: UUID of the notebook to create
    :type nb_uuid: UUID
    """
    execute_query(INSERT_NOTEBOOK, nb_uuid=uuid_bytes(nb_uuid), nb_name=nb_name)


def update_notebook(nb_name, nb_uuid):
    """ Update a notebook

    :param nb_name: New name for the notebook
    :type nb_name: str
    :param nb_uuid: UUID of the notebook to rename
    :type nb_uuid: str
    """
    execute_query(UPDATE_NOTEBOOK_NAME, nb_name=nb_name, nb_uuid=uuid_bytes(nb_uuid))


def delete_notebook(nb_uuid):
    """ Delete a notebook from the database

    :param nb_uuid: UUID of the notebook to delete
    :type nb_uuid: str
    """
    execute_query(DELETE_NOTEBOOK, nb_uuid=uuid_bytes(nb_uuid))


def get_notebook_list():
    """Get a list of all existing notebooks

    :return: [{'uuid': str, 'name' : str}]
    """
    # Execute the query
    buffer = execute_query(SELECT_NOTEBOOK)

    # Return the notebook list
    notebook_list = []

    for notebook in buffer:
        notebook_list.append({'uuid': uuid_string(notebook[0]), 'name': notebook[1]})

    return notebook_list


"""
Experiment table query
"""


def create_experiment(exp_name, exp_uuid, exp_obj, nb_uuid):
    """ Create a new experiment in the main database

    :param exp_name: Experiment name
    :type exp_name: str
    :param exp_uuid: Experiment UUID
    :type exp_uuid: UUID
    :param exp_obj: Experiment objective
    :type exp_obj: str
    :param nb_uuid: UUID of the notebook that contains the experiment
    :type nb_uuid: str
    """
    execute_query(INSERT_EXPERIMENT, exp_uuid=uuid_bytes(exp_uuid),
                  nb_uuid=uuid_bytes(nb_uuid), exp_name=exp_name, exp_objective=exp_obj)


def update_experiment(exp_uuid, name, objective):
    """ Update the name of a notebook

    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :param name: Experiment name
    :type name: str
    :param objective: Experiment objective
    :type objective: str
    """
    execute_query(UPDATE_EXPERIMENT, exp_name=name, exp_objective=objective, exp_uuid=uuid_bytes(exp_uuid))


def delete_experiment(exp_uuid):
    """ Delete an experiment from the database

    :param exp_uuid: UUID of the notebook to delete
    :type exp_uuid: str
    """
    execute_query(DELETE_EXPERIMENT, exp_uuid=uuid_bytes(exp_uuid))


def get_experiment_list_notebook(nb_uuid):
    """ Get the experiment list for a specific notebook

    :param nb_uuid: UUID of the notebook
    :type nb_uuid: str
    :return: [{'uuid': str, 'name' : str, 'objective': str}]
    """
    # Execute the query
    buffer = execute_query(SELECT_NOTEBOOK_EXPERIMENT, nb_uuid=uuid_bytes(nb_uuid))

    # Return the experiment list
    experiement_list = []

    for experiment in buffer:
        experiement_list.append({'uuid': uuid_string(experiment[0]), 'name': experiment[1],
                                 'objective': experiment[2]})

    return experiement_list


def get_experiment_informations(exp_uuid):
    """ Get informations for an experiment

    :param exp_uuid: Experiment UUID
    :type exp_uuid: str
    :return: {'uuid': str, 'name' : str, 'objective': str}
    """
    # Execute query
    buffer = execute_query(SELECT_EXPERIMENT, exp_uuid=uuid_bytes(exp_uuid))

    # Return experiment informations
    return {'name': buffer[0][0], 'objective': buffer[0][1]}
