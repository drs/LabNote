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

MAIN_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/main.labn")
DATASET_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/dataset.labn")

"""
Database query
"""

CREATE_DATASET_TABLE = """
CREATE TABLE dataset (
    dt_uuid     BLOB (16)     PRIMARY KEY,
    name        VARCHAR (255),
    description TEXT
)
"""

CREATE_EXPERIMENT_TABLE = """
CREATE TABLE experiment (
    exp_uuid     BLOB (16)     PRIMARY KEY,
    name         VARCHAR (255) NOT NULL,
    nb_uuid      BLOB (16)     REFERENCES notebook (nb_uuid) ON DELETE CASCADE
                               NOT NULL,
    objective    TEXT,
    body         TEXT,
    date_created DATETIME      DEFAULT (CURRENT_TIMESTAMP),
    date_updated DATETIME
)
"""

CREATE_EXPERIMENT_TABLE_TRIGGER = """
CREATE TRIGGER exp_date_updated
         AFTER UPDATE OF body
            ON experiment
BEGIN
    UPDATE experiment
       SET date_updated = CURRENT_TIMESTAMP
     WHERE NEW.exp_uuid = OLD.exp_uuid;
END;
"""

CREATE_PROJECT_TABLE = """
CREATE TABLE project (
    proj_id     INTEGER       PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR (255) UNIQUE
                              NOT NULL,
    description TEXT
)
"""

CREATE_NOTEBOOK_TABLE = """
CREATE TABLE notebook (
    nb_uuid BLOB (16)     PRIMARY KEY,
    name    VARCHAR (255) NOT NULL,
    proj_id INTEGER       REFERENCES project (proj_id) 
)
"""

CREATE_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    prt_uuid      BLOB (16)     PRIMARY KEY,
    name          VARCHAR (255),
    body          TEXT,
    date_created  DATETIME      DEFAULT (CURRENT_TIMESTAMP),
    date_modified DATETIME
)
"""

CREATE_PROTOCOL_TABLE_TRIGGER = """
CREATE TRIGGER prt_date_updated
         AFTER UPDATE OF body
            ON protocol
BEGIN
    UPDATE protocol
       SET date_updated = CURRENT_TIMESTAMP
     WHERE NEW.prt_uuid = OLD.prt_uuid;
END;
"""

CREATE_REFS_TABLE = """
CREATE TABLE refs (
    ref_uuid  BLOB (16)     PRIMARY KEY,
    title     VARCHAR (255),
    publisher VARCHAR (255),
    year      INTEGER,
    author    VARCHAR (255),
    editor    VARCHAR (255),
    volume    INTEGER,
    address   VARCHAR (255),
    edition   INTEGER,
    journal   VARCHAR (255),
    chapter   VARCHAR (255),
    pages     VARCHAR (16),
    issue     INTEGER
)
"""

CREATE_SAMPLE_NUMBER_TABLE = """
CREATE TABLE sample_number (
    spl_id      INTEGER       PRIMARY KEY AUTOINCREMENT,
    proj_id     INTEGER       REFERENCES project (proj_id),
    description VARCHAR (255),
    treatment_1 VARCHAR (255),
    treatment_2 VARCHAR (255),
    treatment_3 VARCHAR (255),
    treatment_4 VARCHAR (255),
    treatment_5 VARCHAR (255),
    note        TEXT
)
"""

CREATE_TAGS_TABLE = """
CREATE TABLE tags (
    tag_id INTEGER       PRIMARY KEY AUTOINCREMENT,
    name   VARCHAR (255) NOT NULL
                         UNIQUE
)
"""

CREATE_DATASET_TAG_TABLE = """
CREATE TABLE dataset_tag (
    dt_uuid BLOB (16) REFERENCES dataset (dt_uuid) ON DELETE CASCADE
                      NOT NULL,
    tag_id  INTEGER   REFERENCES tags (tag_id) ON DELETE RESTRICT
                      NOT NULL, 
    PRIMARY KEY (dt_uuid, tag_id)
)
"""

CREATE_EXPERIMENT_DATASET_TABLE = """
CREATE TABLE experiment_dataset (
    exp_uuid BLOB (16) REFERENCES experiment (exp_uuid) ON DELETE CASCADE
                       NOT NULL,
    dt_uuid  BLOB (16) REFERENCES dataset (dt_uuid) ON DELETE RESTRICT
                       NOT NULL,
    limits   TEXT, 
    PRIMARY KEY (exp_uuid, dt_uuid)
)
"""

CREATE_EXPERIMENT_PROTOCOL_TABLE = """
CREATE TABLE experiment_protocol (
    exp_uuid BLOB (16) REFERENCES experiment (exp_uuid) ON DELETE CASCADE
                       NOT NULL,
    prt_uuid BLOB (16) REFERENCES protocol (prt_uuid) ON DELETE RESTRICT
                       NOT NULL,
    PRIMARY KEY (exp_uuid, prt_uuid)
)
"""

CREATE_EXPERIMENT_REFS_TABLE = """
CREATE TABLE experiment_references (
    exp_uuid BLOB (16) REFERENCES experiment (exp_uuid) ON DELETE CASCADE
                       NOT NULL,
    ref_uuid BLOB (16) REFERENCES refs (ref_uuid) ON DELETE RESTRICT
                       NOT NULL,
    PRIMARY KEY (exp_uuid, ref_uuid)
)
"""

CREATE_EXPERIMENT_TAG_TABLE = """
CREATE TABLE experiment_tag (
    exp_uuid BLOB (16) REFERENCES experiment (exp_uuid) ON DELETE CASCADE
                       NOT NULL,
    tag_id   INTEGER   REFERENCES tags (tag_id) ON DELETE RESTRICT
                       NOT NULL,
    PRIMARY KEY (exp_uuid, tag_id)
)
"""

CREATE_PROTOCOL_REFS_TABLE = """
CREATE TABLE protocol_references (
    prot_uuid BLOB (16) REFERENCES protocol (prt_uuid) ON DELETE CASCADE
                        NOT NULL,
    ref_uuid  BLOB (16) REFERENCES refs (ref_uuid) ON DELETE RESTRICT
                        NOT NULL,
    PRIMARY KEY (prot_uuid, ref_uuid)
)
"""

CREATE_PROTOCOL_TAG_TABLE = """
CREATE TABLE protocol_tag (
    prot_uuid BLOB (16) REFERENCES protocol (prt_uuid) ON DELETE CASCADE
                        NOT NULL,
    tag_id    INTEGER   REFERENCES tags (tag_id) ON DELETE RESTRICT
                        NOT NULL,
    PRIMARY KEY (prot_uuid, tag_id)
)
"""

CREATE_REFS_TAG_TABLE = """
CREATE TABLE refs_tag (
    ref_uuid BLOB (16) REFERENCES refs (ref_uuid) ON DELETE CASCADE
                       NOT NULL,
    tag_id INTEGER   REFERENCES tags (tag_id) ON DELETE RESTRICT
                       NOT NULL,
    PRIMARY KEY (ref_uuid, tag_id)
)
"""

SELECT_NOTEBOOK = """
SELECT nb_uuid, name FROM notebook ORDER BY name ASC
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (nb_uuid, name) VALUES (:nb_uuid, :name)
"""

INSERT_EXPERIMENT = """
INSERT INTO experiment (exp_uuid, nb_uuid, name, objective) 
VALUES (:exp_uuid, :nb_uuid, :name, :objective)
"""

SELECT_NOTEBOOK_EXPERIMENT = """
SELECT exp_uuid, name, objective FROM experiment WHERE nb_uuid = :nb_uuid
"""

UPDATE_NOTEBOOK_NAME = """
UPDATE notebook SET name = :name WHERE nb_uuid = :nb_uuid
"""

DELETE_NOTEBOOK = """
DELETE FROM notebook WHERE nb_uuid = :nb_uuid
"""

SELECT_EXPERIMENT = """
SELECT name, objective FROM experiment WHERE exp_uuid = :exp_uuid
"""

UPDATE_EXPERIMENT = """
UPDATE experiment SET name = :name, objective = :objective WHERE  exp_uuid = :exp_uuid
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
    cursor.execute(CREATE_DATASET_TABLE)
    cursor.execute(CREATE_EXPERIMENT_TABLE)
    cursor.execute(CREATE_EXPERIMENT_TABLE_TRIGGER)
    cursor.execute(CREATE_PROJECT_TABLE)
    cursor.execute(CREATE_NOTEBOOK_TABLE)
    cursor.execute(CREATE_PROTOCOL_TABLE)
    cursor.execute(CREATE_PROTOCOL_TABLE_TRIGGER)
    cursor.execute(CREATE_REFS_TABLE)
    cursor.execute(CREATE_SAMPLE_NUMBER_TABLE)
    cursor.execute(CREATE_TAGS_TABLE)
    cursor.execute(CREATE_DATASET_TAG_TABLE)
    cursor.execute(CREATE_EXPERIMENT_DATASET_TABLE)
    cursor.execute(CREATE_EXPERIMENT_PROTOCOL_TABLE)
    cursor.execute(CREATE_EXPERIMENT_REFS_TABLE)
    cursor.execute(CREATE_EXPERIMENT_TAG_TABLE)
    cursor.execute(CREATE_PROTOCOL_REFS_TABLE)
    cursor.execute(CREATE_PROTOCOL_TAG_TABLE)
    cursor.execute(CREATE_REFS_TAG_TABLE)
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


def create_notebook(name, nb_uuid):
    """ Create a new notebook

    :param name: Name of the notebook to create
    :type name: str
    :param nb_uuid: UUID of the notebook to create
    :type nb_uuid: UUID
    """
    execute_query(INSERT_NOTEBOOK, nb_uuid=uuid_bytes(nb_uuid), name=name)


def update_notebook(name, nb_uuid):
    """ Update a notebook

    :param name: New name for the notebook
    :type name: str
    :param nb_uuid: UUID of the notebook to rename
    :type nb_uuid: str
    """
    execute_query(UPDATE_NOTEBOOK_NAME, name=name, nb_uuid=uuid_bytes(nb_uuid))


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


def create_experiment(name, exp_uuid, obj, nb_uuid):
    """ Create a new experiment in the main database

    :param name: Experiment name
    :type name: str
    :param exp_uuid: Experiment UUID
    :type exp_uuid: UUID
    :param obj: Experiment objective
    :type obj: str
    :param nb_uuid: UUID of the notebook that contains the experiment
    :type nb_uuid: str
    """
    execute_query(INSERT_EXPERIMENT, exp_uuid=uuid_bytes(exp_uuid),
                  nb_uuid=uuid_bytes(nb_uuid), name=name, objective=obj)


def update_experiment(exp_uuid, name, objective):
    """ Update the name of a notebook

    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :param name: Experiment name
    :type name: str
    :param objective: Experiment objective
    :type objective: str
    """
    execute_query(UPDATE_EXPERIMENT, name=name, objective=objective, exp_uuid=uuid_bytes(exp_uuid))


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
