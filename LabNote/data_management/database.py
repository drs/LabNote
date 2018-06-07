# Python import
import sqlite3
import os
import logging

# Project import
from data_management import directory
from common import logs

MAIN_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/labnote.db")
PROTOCOL_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/protocols.db")

CREATE_NOTEBOOK_TABLE = """
CREATE TABLE notebook (
    notebook_id     INTEGER         PRIMARY KEY   AUTOINCREMENT,
    name            VARCHAR (255)   NOT NULL      UNIQUE, 
    uuid            CHAR (36)       UNIQUE        NOT NULL
)"""

CREATE_EXPERIMENT_TABLE = """
CREATE TABLE experiment (
    experiment_id       INTEGER       PRIMARY KEY   AUTOINCREMENT,
    experiment_name     VARCHAR (255) NOT NULL      UNIQUE,
    experiment_uuid     CHAR (36)     NOT NULL      UNIQUE,
    notebook_id         INTEGER       NOT NULL      REFERENCES notebook (notebook_id)
)"""

CREATE_EXPERIMENT_INDEX = """
CREATE UNIQUE INDEX experiment_uuid ON experiment (
    experiment_uuid ASC
)"""

CREATE_DATASET_TABLE = """
CREATE TABLE dataset (
    dataset_id      INTEGER     PRIMARY KEY   AUTOINCREMENT,
    dataset_uuid    CHAR (36)   NOT NULL      UNIQUE,
    name            VARCHAR (255) 
)"""

CREATE_DATASET_INDEX = """
CREATE UNIQUE INDEX dataset_index ON dataset (
    dataset_uuid
)"""

CREATE_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    protocol_id     INTEGER   PRIMARY KEY   AUTOINCREMENT,
    protocol_uuid   CHAR (36) NOT NULL      UNIQUE,
    name            VARCHAR (255)
)
"""

CREATE_PROTOCOL_INDEX = """
CREATE UNIQUE INDEX protocol_index ON protocol (
    protocol_uuid
)"""

CREATE_EXPERIMENT_DATASET_TABLE = """
CREATE TABLE experiment_dataset (
    experiment_id INTEGER REFERENCES experiment (experiment_id)  NOT NULL,
    dataset_id    INTEGER REFERENCES dataset (dataset_id)       NOT NULL
)"""

CREATE_EXPERIMENT_DATASET_INDEX = """
CREATE UNIQUE INDEX experiment_dataset_index ON experiment_dataset (
    experiment_id ASC,
    dataset_id ASC
)"""

CREATE_EXPERIMENT_PROTOCOL_TABLE = """
CREATE TABLE experiment_protocol (
    experiment_id INTEGER REFERENCES experiment (experiment_id)     NOT NULL,
    protocol_id   INTEGER REFERENCES protocol (protocol_id)         NOT NULL
)"""

CREATE_EXPERIMENT_PROTOCOL_INDEX = """
CREATE UNIQUE INDEX experiment_protocol_index ON experiment_protocol (
    experiment_id ASC,
    protocol_id ASC
)"""

CREATE_PROTOCOL_DB_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    protocol_id       INTEGER       PRIMARY KEY AUTOINCREMENT,
    protocol_uuid     CHAR (36)     NOT NULL
                                    UNIQUE,
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
    research_field_id INTEGER           PRIMARY KEY     AUTOINCREMENT,
    name              VARCHAR (255)     NOT NULL        UNIQUE
)"""

SELECT_NOTEBOOK_NAME = """
SELECT notebook_id, name FROM notebook
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (name, uuid) VALUES ('{}', '{}')
"""

print("database logging")
logs.init_logging()


def create_notebook(nb_name, nb_uuid):
    """ Create a new notebook """
    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    cursor = conn.cursor()

    query = INSERT_NOTEBOOK.format(nb_name, nb_uuid)
    try:
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        logging.info("Creating a new notebook ({}) in the labnote.db".format(nb_name))
        logging.exception(str(e))
        raise
    finally:
        if conn:
            conn.close()


def get_notebook_list():
    """Get a list of all existing notebooks

    :return: List of dictionary of name and id of the notebooks
    """
    # Prepare the connection
    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    cursor = conn.cursor()

    # Select notebook list from database
    buffer = None

    try:
        cursor.execute(SELECT_NOTEBOOK_NAME)
        buffer = cursor.fetchall()
    except sqlite3.Error as e:
        logging.info("Getting name and id of all notebooks from labnote.db")
        logging.exception(str(e))
        raise
    finally:
        if conn:
            conn.close()

    # Prepare the return format

    notebook_list = []

    for notebook in buffer:
        notebook_list.append({'id': notebook[0], 'name': notebook[1]})

    return notebook_list

def create_main_database():
    """ Create the labnote database """
    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    conn.isolation_level = None

    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")
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
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")
        
        logging.info("Creating the labnote.db file")
        logging.exception(str(e))
        raise
    finally:
        if conn:
            conn.close()


def create_protocol_db():
    """ Create the protocol database """
    conn = sqlite3.connect(PROTOCOL_DATABASE_FILE_PATH)
    conn.isolation_level = None

    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")
        cursor.execute(CREATE_PROTOCOL_DB_RESEACH_FIELD_TABLE)
        cursor.execute(CREATE_PROTOCOL_DB_PROTOCOL_TABLE)
        cursor.execute(CREATE_PROTOCOL_DB_UPDATE_DATE_TRIGGER)
        cursor.execute("COMMIT")
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")

        logging.info("Creating the protocol.db file")
        logging.exception(str(e))
        raise
    finally:
        if conn:
            conn.close()
