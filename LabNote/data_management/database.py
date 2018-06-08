# Python import
import sqlite3
import os
import logging

# PyQt import
from PyQt5.QtWidgets import QMessageBox

# Project import
from LabNote.data_management import directory
from LabNote.common import logs

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


def create_notebook(nb_name, nb_uuid, silent=False):
    """ Create a new notebook

    :param silent: Hide the messagebox if true
    :type silent: bool
    :returns: True if the notebook was created and false otherwise
    """

    conn = None
    query = INSERT_NOTEBOOK.format(nb_name, nb_uuid)

    try:
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        cursor = conn.cursor()

        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        # Log error
        logging.info("Creating a new notebook ({}) in the labnote.db".format(nb_name))
        logging.exception(str(e))

        # Warn the user
        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Notebook cannot be created")
            message.setInformativeText("An error occurred during the notebook creation in the database.")
            message.setDetailedText(str(e))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        return False
    finally:
        if conn:
            conn.close()

    return True


def get_notebook_list(silent=False):
    """Get a list of all existing notebooks

    :param silent: Hide the messagebox if true
    :type silent: bool
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

        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the notebook list")
            message.setInformativeText("An error occurred while getting the notebook list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
    finally:
        if conn:
            conn.close()

    # Prepare the return format

    notebook_list = []

    for notebook in buffer:
        notebook_list.append({'id': notebook[0], 'name': notebook[1]})

    return notebook_list


def create_main_database(silent=False):
    """ Create the labnote database

    :param silent: Hide the messagebox if true
    :type silent: bool
    """

    conn = None

    try:
        conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
        conn.isolation_level = None
        cursor = conn.cursor()

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
    except sqlite3.Error as exception:
        # Warn the user
        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Main database cannot be created")
            message.setInformativeText("An error occurred during the creation of the main database. "
                                   "The program will now close.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Try to cleanup the main directory
        try:
            directory.cleanup_main_directory()
        except:
            raise  # Raise any possible exception that can happen at this point

        raise
    finally:
        if conn:
            conn.close()


def create_protocol_db(silent=False):
    """ Create the protocole database

    :param silent: Hide the messagebox if true
    :type silent: bool
    """

    conn = None

    try:
        conn = sqlite3.connect(PROTOCOL_DATABASE_FILE_PATH)
        conn.isolation_level = None

        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(CREATE_PROTOCOL_DB_RESEACH_FIELD_TABLE)
        cursor.execute(CREATE_PROTOCOL_DB_PROTOCOL_TABLE)
        cursor.execute(CREATE_PROTOCOL_DB_UPDATE_DATE_TRIGGER)
        cursor.execute("COMMIT")
    except sqlite3.Error as exception:
        # Warn the user
        if not silent:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Protocols database cannot be created")
            message.setInformativeText("An error occurred during the creation of the protocols database. "
                                   "The program will now close.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Try to cleanup the main directory
        try:
            directory.cleanup_main_directory()
        except:
            raise  # Raise any possible exception that can happen at this point

        raise
    finally:
        if conn:
            conn.close()
