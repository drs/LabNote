# Python import
import sqlite3
import os
from collections import namedtuple

# Project import
from labnote.utils import directory
from labnote.utils.conversion import uuid_bytes, uuid_string
from labnote.core import data, sqlite_error

"""
Database path
"""

MAIN_DATABASE_FILE_PATH = os.path.join(directory.DEFAULT_MAIN_DIRECTORY_PATH + "/main.labn")

"""
Database query
"""

CREATE_DATASET_TABLE = """
CREATE TABLE dataset (
    dt_uuid BLOB (16)     PRIMARY KEY
                          UNIQUE,
    name    VARCHAR (255) NOT NULL,
    dt_key  VARCHAR (255) UNIQUE
                          NOT NULL,
    nb_uuid BLOB (16)     REFERENCES notebook (nb_uuid) ON DELETE CASCADE,
    UNIQUE (
        dt_key,
        nb_uuid
    )
)
"""

CREATE_EXPERIMENT_TABLE = """
CREATE TABLE experiment (
    exp_uuid     BLOB (16)     PRIMARY KEY
                               UNIQUE,
    exp_key      VARCHAR (255),
    name         VARCHAR (255) NOT NULL,
    nb_uuid      BLOB (16)     REFERENCES notebook (nb_uuid) ON DELETE CASCADE
                               NOT NULL,
    description  TEXT,
    date_created DATETIME      DEFAULT (CURRENT_TIMESTAMP),
    date_updated DATETIME, 
    UNIQUE (
        exp_key,
        exp_uuid
    )
)
"""

CREATE_EXPERIMENT_TABLE_TRIGGER = """
CREATE TRIGGER exp_date_updated
         AFTER UPDATE
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
    nb_uuid BLOB (16)     PRIMARY KEY
                          UNIQUE,
    name    VARCHAR (255) NOT NULL,
    proj_id INTEGER       REFERENCES project (proj_id) ON DELETE RESTRICT,
    UNIQUE (
        name,
        proj_id
    )
)
"""

CREATE_PROTOCOL_TABLE = """
CREATE TABLE protocol (
    prt_uuid       BLOB (16)     PRIMARY KEY
                                 UNIQUE,
    prt_key        VARCHAR (255) UNIQUE
                                 NOT NULL,
    name           VARCHAR (255),
    description    TEXT,
    date_created   DATETIME      DEFAULT (CURRENT_TIMESTAMP),
    date_updated   DATETIME,
    category_id    INTEGER       REFERENCES category (category_id) ON DELETE RESTRICT
                                 NOT NULL,
    subcategory_id INTEGER       REFERENCES subcategory (subcategory_id) ON DELETE RESTRICT
)
"""

CREATE_PROTOCOL_TABLE_TRIGGER = """
CREATE TRIGGER prt_date_updated
         AFTER UPDATE
            ON protocol
BEGIN
    UPDATE protocol
       SET date_updated = CURRENT_TIMESTAMP
     WHERE NEW.prt_uuid = OLD.prt_uuid;
END;

"""

CREATE_CATEGORY_TABLE = """
CREATE TABLE category (
    category_id INTEGER       PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR (255) UNIQUE
                              NOT NULL
)
"""

CREATE_SUBCATEGORY_TABLE = """
CREATE TABLE subcategory (
    subcategory_id INTEGER       PRIMARY KEY AUTOINCREMENT,
    name           VARCHAR (255) NOT NULL,
    category_id    INTEGER       REFERENCES category (category_id) ON DELETE RESTRICT
                                 NOT NULL,
    UNIQUE (name, category_id)
)
"""

CREATE_REFS_TABLE = """
CREATE TABLE refs (
    ref_uuid       BLOB (16)     PRIMARY KEY
                                 UNIQUE,
    ref_key        VARCHAR (255) NOT NULL
                                 UNIQUE,
    ref_type       INTEGER       NOT NULL,
    file_attached  BOOLEAN       NOT NULL
                                 DEFAULT FALSE,
    title          VARCHAR (255),
    publisher      VARCHAR (255),
    year           INTEGER,
    author         VARCHAR (255),
    editor         VARCHAR (255),
    volume         INTEGER,
    address        VARCHAR (255),
    edition        INTEGER,
    journal        VARCHAR (255),
    chapter        VARCHAR (255),
    pages          VARCHAR (16),
    issue          INTEGER,
    description    TEXT,
    abstract       TEXT,
    subcategory_id INTEGER       REFERENCES subcategory (subcategory_id) ON DELETE RESTRICT,
    category_id    INTEGER       REFERENCES category (category_id) ON DELETE RESTRICT
                                 NOT NULL
)
"""

CREATE_SAMPLE_TABLE = """
CREATE TABLE sample (
    spl_id      INTEGER       PRIMARY KEY AUTOINCREMENT,
    custom_id   VARCHAR (255),
    project VARCHAR (255),
    description VARCHAR (255),
    treatment_1 VARCHAR (255),
    treatment_2 VARCHAR (255),
    treatment_3 VARCHAR (255),
    treatment_4 VARCHAR (255),
    treatment_5 VARCHAR (255),
    origin      VARCHAR (255),
    location    VARCHAR (255),
    spl_date    VARCHAR (24),
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

CREATE_EXPERIMENT_DATASET_TABLE = """
CREATE TABLE experiment_dataset (
    exp_uuid BLOB (16) REFERENCES experiment (exp_uuid) ON DELETE CASCADE
                       NOT NULL,
    dt_uuid  BLOB (16) REFERENCES dataset (dt_uuid) ON DELETE RESTRICT
                       NOT NULL,
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
SELECT nb_uuid, name, proj_id FROM notebook ORDER BY name ASC
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (nb_uuid, name, proj_id) VALUES (:nb_uuid, :name, :proj_id)
"""

UPDATE_NOTEBOOK = """
UPDATE notebook SET 
name = :name, 
proj_id = :proj_id
 WHERE nb_uuid = :nb_uuid
"""

DELETE_NOTEBOOK = """
DELETE FROM notebook WHERE nb_uuid = :nb_uuid
"""

SELECT_PROJECT = """
SELECT proj_id, name, description FROM project ORDER BY name ASC
"""

SELECT_PROJECT_SEARCH = """
SELECT proj_id, name, description FROM project WHERE name LIKE :name ORDER BY name ASC
"""

INSERT_PROJECT = """
INSERT INTO project (name, description) VALUES (:name, :description)
"""

UPDATE_PROJECT = """
UPDATE project SET name = :name, description = :description WHERE proj_id = :proj_id
"""

DELETE_PROJECT = """
DELETE FROM project WHERE proj_id = :proj_id
"""

LAST_INSERT_ROWID = """
SELECT last_insert_rowid()
"""

INSERT_CATEGORY = """
INSERT INTO category (name) VALUES (:name)
"""

UPDATE_CATEGORY = """
UPDATE category SET name = :name WHERE category_id = :category_id
"""

DELETE_CATEGORY = """
DELETE FROM category WHERE category_id = :category_id
"""

INSERT_SUBCATEGORY = """
INSERT INTO subcategory (name, category_id) VALUES (:name, :category_id)
"""

UPDATE_SUBCATEGORY = """
UPDATE subcategory SET name = :name, category_id = :category_id WHERE subcategory_id = :subcategory_id
"""

DELETE_SUBCATEGORY = """
DELETE FROM subcategory WHERE subcategory_id = :subcategory_id
"""

SELECT_CATEGORY = """
SELECT category_id, name FROM category ORDER BY name ASC
"""

SELECT_SUBCATEGORY = """
SELECT subcategory_id, name, category_id FROM subcategory ORDER BY category_id ASC, name ASC
"""

SELECT_REFS = """
SELECT ref_uuid, title, author, year, category_id, subcategory_id FROM refs ORDER BY category_id ASC, 
subcategory_id ASC
"""

INSERT_REF = """
INSERT INTO refs (ref_uuid, ref_key, ref_type, file_attached, title, publisher, year, author, editor, volume, address, 
edition, journal, chapter, pages, issue, description, abstract, subcategory_id, category_id) 
VALUES 
(:ref_uuid, :ref_key, :ref_type, :file_attached, :title, :publisher, :year, :author, :editor, :volume, :address, 
:edition, :journal, :chapter, :pages, :issue, :description, :abstract, :subcategory_id, :category_id)
"""

SELECT_REF = """
SELECT ref_uuid, ref_key, ref_type, file_attached, title, publisher, year, author, editor, volume, address, 
edition, journal, chapter, pages, issue, description, abstract FROM refs
WHERE ref_uuid = :ref_uuid
"""

UPDATE_REF = """
UPDATE refs SET 
  ref_key = :ref_key,
  ref_type = :ref_type,
  title = :title,
  publisher = :publisher,
  year = :year,
  author = :author,
  editor = :editor,
  volume = :volume,
  address = :address,
  edition = :edition,
  journal = :journal,
  chapter = :chapter,
  pages = :pages,
  issue = :issue,
  description = :description,
  abstract = :abstract
WHERE ref_uuid = :ref_uuid
"""

DELETE_REF = """
DELETE FROM refs WHERE ref_uuid=:ref_uuid
"""

UPDATE_REFERENCE_CATEGORY = """
UPDATE refs SET 
category_id = :category_id,
subcategory_id = :subcategory_id
WHERE ref_uuid = :ref_uuid
"""

UPDATE_REFERENCE_FILE = """
UPDATE refs SET
file_attached = :file_attached
WHERE ref_uuid = :ref_uuid
"""

INSERT_TAG = """
INSERT OR IGNORE INTO tags (name) VALUES (:name)
"""

INSERT_TAG_REF = """
INSERT OR IGNORE INTO refs_tag (ref_uuid, tag_id) VALUES (:ref_uuid, (SELECT tag_id FROM tags WHERE name = :name))
"""

SELECT_REFERENCE_TAG = """
SELECT tag_id FROM refs_tag WHERE ref_uuid=:ref_uuid
"""

DELETE_TAG = """
DELETE FROM tags WHERE name = :name
"""

DELETE_TAG_ID = """
DELETE FROM tags WHERE tag_id=:tag_id
"""

DELETE_TAG_REF = """
DELETE FROM refs_tag WHERE tag_id = (SELECT tag_id FROM tags WHERE name = :name) AND ref_uuid = :ref_uuid
"""

SELECT_TAG = """
SELECT name FROM tags
"""

SELECT_REFERENCE_TAG_NAME = """
SELECT name FROM tags WHERE tag_id = (SELECT tag_id FROM refs_tag WHERE ref_uuid=:ref_uuid)
"""

SELECT_SAMPLE = """
SELECT spl_id, custom_id, project, description, treatment_1, treatment_2, treatment_3, treatment_4, treatment_5,
origin, location, spl_date, note
FROM sample ORDER BY spl_id ASC
"""

SELECT_SAMPLE_SEARCH = """
SELECT spl_id, custom_id, project, description, treatment_1, treatment_2, treatment_3, treatment_4, treatment_5,
origin, location, spl_date, note
FROM sample 
WHERE custom_id == :search OR description LIKE :search 
OR treatment_1 LIKE :search OR treatment_2 LIKE :search OR treatment_3 LIKE :search 
OR origin LIKE :search
ORDER BY spl_id ASC
"""

INSERT_SAMPLE = """
INSERT INTO sample (custom_id, project, description, treatment_1, treatment_2, treatment_3, treatment_4, treatment_5, 
origin, location, spl_date, note) VALUES (:custom_id, :project, :description, :treatment_1, :treatment_2, :treatment_3, 
:treatment_4, :treatment_5, :origin, :location, :spl_date, :note)
"""

CREATE_SAMPLE = """
INSERT INTO sample (custom_id, project, description) 
VALUES (:custom_id, :project, :description)
"""

UPDATE_SAMPLE_CUSTOM_ID = """
UPDATE sample SET custom_id = :custom_id WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_PROJECT = """
UPDATE sample SET project = :project WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_DESCRIPTION = """
UPDATE sample SET description = :description WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_TREATMENT_1 = """
UPDATE sample SET treatment_1 = :treatment_1 WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_TREATMENT_2 = """
UPDATE sample SET treatment_2 = :treatment_2 WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_TREATMENT_3 = """
UPDATE sample SET treatment_3 = :treatment_3 WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_TREATMENT_4 = """
UPDATE sample SET treatment_4 = :treatment_4 WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_TREATMENT_5 = """
UPDATE sample SET treatment_5 = :treatment_5 WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_ORIGIN = """
UPDATE sample SET origin = :origin WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_LOCATION = """
UPDATE sample SET location = :location WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_DATE = """
UPDATE sample SET spl_date = :spl_date WHERE spl_id = :spl_id
"""

UPDATE_SAMPLE_NOTE = """
UPDATE sample SET note = :note WHERE spl_id = :spl_id
"""

DELETE_SAMPLE = """
DELETE FROM sample WHERE spl_id = :spl_id
"""

SELECT_DATASET = """
SELECT dt_uuid, name, dt_key, nb_uuid FROM dataset
"""

INSERT_DATASET = """
INSERT INTO dataset (dt_uuid, name, dt_key, nb_uuid) VALUES (:dt_uuid, :name, :dt_key, :nb_uuid)
"""

UPDATE_DATASET = """
UPDATE dataset SET name = :name, dt_key=:dt_key WHERE dt_uuid = :dt_uuid
"""

DELETE_DATASET = """
DELETE FROM dataset WHERE dt_uuid = :dt_uuid
"""

SELECT_PROTOCOL_LIST = """
SELECT prt_uuid, name, category_id, subcategory_id FROM protocol
"""

INSERT_PROTOCOL = """
INSERT INTO protocol (prt_uuid, prt_key, name, category_id, subcategory_id) VALUES 
(:prt_uuid, :prt_key, :name, :category_id, :subcategory_id)
"""

UPDATE_PROTOCOL = """
UPDATE protocol SET 
  prt_key=:prt_key, 
  name=:name,
  description=:description
WHERE prt_uuid=:prt_uuid
"""

UPDATE_PROTOCOL_CATEGORY = """
UPDATE protocol SET
  category_id=:category_id, 
  subcategory_id=:subcategory_id
WHERE prt_uuid=:prt_uuid
"""

DELETE_PROTOCOL = """
DELETE FROM protocol WHERE prt_uuid=:prt_uuid
"""

SELECT_PROTOCOL = """
SELECT prt_key, name, description, date_created, date_updated FROM protocol WHERE prt_uuid=:prt_uuid
"""

SELECT_REFERENCE_COMPLETER_LIST = """
SELECT ref_uuid, ref_key, author, year, title FROM refs
"""

SELECT_PROTOCOL_COMPLETER_LIST = """
SELECT prt_uuid, prt_key, name FROM protocol
"""

SELECT_DATASET_COMPLETER_LIST = """
SELECT dt_uuid, dt_key, name FROM dataset
"""

INSERT_TAG_PROTOCOL = """
INSERT OR IGNORE INTO protocol_tag (prot_uuid, tag_id) 
VALUES (:prot_uuid, (SELECT tag_id FROM tags WHERE name = :name))
"""

INSERT_REF_PROTOCOL = """
INSERT OR IGNORE INTO protocol_references (prot_uuid, ref_uuid) VALUES (:prot_uuid, :ref_uuid)
"""

SELECT_PROTOCOL_TAG_NAME = """
SELECT name FROM tags WHERE tag_id = (SELECT tag_id FROM protocol_tag WHERE prot_uuid=:prot_uuid)
"""

SELECT_PROTOCOL_REFERENCE_UUID = """
SELECT ref_uuid FROM protocol_references WHERE prot_uuid=:prot_uuid
"""

DELETE_TAG_PROTOCOL = """
DELETE FROM protocol_tag WHERE tag_id = (SELECT tag_id FROM tags WHERE name=:name) AND prot_uuid=:prot_uuid
"""

DELETE_REF_PROTOCOL = """
DELETE FROM protocol_references WHERE ref_uuid=:ref_uuid AND prot_uuid=:prot_uuid
"""

SELECT_PROTOCOL_TAG = """
SELECT tag_id FROM protocol_tag WHERE prot_uuid=:prot_uuid
"""

SELECT_EXPERIMENT_KEY_NOTEBOOK = """
SELECT exp_key FROM experiment WHERE nb_uuid=:nb_uuid
"""

SELECT_EXPERIMENT_NOTEBOOK = """
SELECT exp_uuid, name, exp_key FROM experiment WHERE nb_uuid=:nb_uuid ORDER BY exp_key ASC
"""

INSERT_EXPERIMENT = """
INSERT INTO experiment (exp_uuid, exp_key, name, nb_uuid, description) VALUES 
(:exp_uuid, :exp_key, :name, :nb_uuid, :description)
"""

UPDATE_EXPERIMENT = """
UPDATE experiment SET
exp_key=:exp_key,
name=:name,
description=:description
WHERE exp_uuid=:exp_uuid
"""

DELETE_EXPERIMENT = """
DELETE FROM experiment WHERE exp_uuid=:exp_uuid
"""

SELECT_EXPERIMENT = """
SELECT exp_key, name, description, date_created, date_updated FROM experiment WHERE exp_uuid=:exp_uuid
"""

INSERT_TAG_EXPERIMENT = """
INSERT OR IGNORE INTO experiment_tag (exp_uuid, tag_id) 
VALUES (:exp_uuid, (SELECT tag_id FROM tags WHERE name = :name))
"""

DELETE_TAG_EXPERIMENT = """
DELETE FROM experiment_tag WHERE tag_id = (SELECT tag_id FROM tags WHERE name=:name) AND exp_uuid=:exp_uuid
"""


INSERT_REF_EXPERIMENT = """
INSERT OR IGNORE INTO experiment_references (exp_uuid, ref_uuid) VALUES (:exp_uuid, :ref_uuid)
"""

DELETE_REF_EXPERIMENT = """
DELETE FROM experiment_references WHERE ref_uuid=:ref_uuid AND exp_uuid=:exp_uuid
"""

INSERT_DATASET_EXPERIMENT = """
INSERT OR IGNORE INTO experiment_dataset (exp_uuid, dt_uuid) VALUES (:exp_uuid, :dt_uuid)
"""

DELETE_DATASET_EXPERIMENT = """
DELETE FROM experiment_dataset WHERE dt_uuid =:dt_uuid AND exp_uuid=:exp_uuid
"""

INSERT_PROTOCOL_EXPERIMENT = """
INSERT OR IGNORE INTO experiment_protocol (exp_uuid, prt_uuid) VALUES (:exp_uuid, :prt_uuid)
"""

DELETE_PROTOCOL_EXPERIMENT = """
DELETE FROM experiment_protocol WHERE prt_uuid=:prt_uuid AND exp_uuid=:exp_uuid
"""

SELECT_EXPERIMENT_TAG_NAME = """
SELECT name FROM tags WHERE tag_id = (SELECT tag_id FROM experiment_tag WHERE exp_uuid=:exp_uuid)
"""

SELECT_EXPERIMENT_REFERENCE_UUID = """
SELECT ref_uuid FROM experiment_references WHERE exp_uuid=:exp_uuid
"""

SELECT_EXPERIMENT_DATASET_UUID = """
SELECT dt_uuid FROM experiment_dataset WHERE exp_uuid=:exp_uuid
"""

SELECT_EXPERIMENT_PROTOCOL_UUID = """
SELECT prt_uuid FROM experiment_protocol WHERE exp_uuid=:exp_uuid
"""

SELECT_EXPERIMENT_TAG = """
SELECT tag_id FROM experiment_tag WHERE exp_uuid=:exp_uuid
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
    cursor.execute(CREATE_CATEGORY_TABLE)
    cursor.execute(CREATE_SUBCATEGORY_TABLE)
    cursor.execute(CREATE_REFS_TABLE)
    cursor.execute(CREATE_SAMPLE_TABLE)
    cursor.execute(CREATE_TAGS_TABLE)
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
    """ Execute an sqlite query to the main database

    :param query: sqlite3 query
    :type query: str
    :param kwargs: query named placeholder content
    :return: cursor.fetchall result
    """
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute(query, kwargs)
        buffer = cursor.fetchall()

    return buffer


def execute_query_last_insert_rowid(query, **kwargs):
    """ Execute an sqlite query to the main database and return the last inserted rowid

    :param query: sqlite3 query
    :type query: str
    :param kwargs: query named placeholder content
    :returns: LAST_INSERT_ROWID() result
    """

    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    conn.isolation_level = None
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("BEGIN")
    cursor.execute(query, kwargs)
    cursor.execute(LAST_INSERT_ROWID)
    buffer = cursor.fetchall()[0][0]
    cursor.execute("COMMIT")
    conn.close()

    return buffer


"""
Process functions
"""


def process_tag(cursor, insert_list, current_list, insert, delete, value):
    if insert_list:
        # Create missing tags
        for tag in insert_list:
            if current_list:
                if tag not in current_list[0]:
                    cursor.execute(INSERT_TAG, {'name': tag})
                    value['name'] = tag
                    cursor.execute(insert, value)
            else:
                cursor.execute(INSERT_TAG, {'name': tag})
                value['name'] = tag
                cursor.execute(insert, value)
        # Remove removed tags
        if current_list:
            for tag in current_list[0]:
                if tag not in insert_list:
                    value['name'] = tag
                    cursor.execute(delete, value)

                    # Ignore foreign key exception
                    # They are expected to occur if the tag is used elsewhere
                    try:
                        cursor.execute(DELETE_TAG, {'name': tag})
                    except sqlite3.Error as expt:
                        error_code = sqlite_error.sqlite_err_handler(str(expt))
                        if error_code == sqlite_error.FOREIGN_KEY_CODE:
                            pass
                        else:
                            raise
    else:
        # Remove removed tags
        if current_list:
            for tag in current_list[0]:
                if tag not in insert_list:
                    value['name'] = tag
                    cursor.execute(delete, value)

                    # Ignore foreign key exception
                    # They are expected to occur if the tag is used elsewhere
                    try:
                        cursor.execute(DELETE_TAG, {'name': tag})
                    except sqlite3.Error as expt:
                        error_code = sqlite_error.sqlite_err_handler(str(expt))
                        if error_code == sqlite_error.FOREIGN_KEY_CODE:
                            pass
                        else:
                            raise


def process_key(cursor, insert_list, current_list, insert, delete, value, key):
    if insert_list:
        # Create missing key
        for reference in insert_list:
            if current_list:
                if data.uuid_bytes(reference) not in current_list[0]:
                    value[key] = data.uuid_bytes(reference)
                    cursor.execute(insert, value)
            else:
                value[key] = data.uuid_bytes(reference)
                cursor.execute(insert, value)
        # Remove removed key
        if current_list:
            for reference in current_list[0]:
                if data.uuid_string(reference) not in insert_list:
                    value[key] = reference
                    cursor.execute(delete, value)
    else:
        # Remove removed reference
        if current_list:
            for reference in current_list[0]:
                if data.uuid_string(reference) not in insert_list:
                    value[key] = reference
                    cursor.execute(delete, value)


"""
Notebook table query
"""


def create_notebook(name, nb_uuid, proj_id):
    """ Create a new notebook

    :param name: Name of the notebook to create
    :type name: str
    :param nb_uuid: UUID of the notebook to create
    :type nb_uuid: UUID
    :param proj_id: Project id for the notebook
    :type proj_id: int
    """
    execute_query(INSERT_NOTEBOOK, nb_uuid=uuid_bytes(nb_uuid), name=name, proj_id=proj_id)


def update_notebook(name, nb_uuid, proj_id):
    """ Update a notebook

    :param name: New name for the notebook
    :type name: str
    :param nb_uuid: UUID of the notebook to rename
    :type nb_uuid: str
    """
    execute_query(UPDATE_NOTEBOOK, name=name, nb_uuid=uuid_bytes(nb_uuid), proj_id=proj_id)


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


def select_notebook_project():
    """ Select all the notebook """

    # Execute the query
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.isolation_level = None
        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(SELECT_PROJECT)
        project_buffer = cursor.fetchall()
        cursor.execute(SELECT_NOTEBOOK)
        notebook_buffer = cursor.fetchall()
        cursor.execute("END")

    # Return the references list
    Project = namedtuple('Project', ['id', 'name', 'notebook'])
    Notebook = namedtuple('Notebook', ['uuid', 'name'])

    project_list = []

    if project_buffer:
        for project in project_buffer:
            project_id = project[0]
            project_name = project[1]

            notebook_list = []
            if notebook_buffer:
                for notebook in notebook_buffer:
                    if notebook[2] == project_id:
                        notebook_uuid = data.uuid_string(notebook[0])
                        notebook_name = notebook[1]
                        notebook_list.append(Notebook(notebook_uuid, notebook_name))

            project_list.append(Project(project_id, project_name, notebook_list))
    return project_list


"""
Project table query
"""


def select_project_list(search=None):
    """ Get a list of all existing project

    :param search: Search string
    :type search: str
    :return: [{'id': int, 'name': str, 'description': str}]
    """

    # Execute the query
    if search:
        buffer = execute_query(SELECT_PROJECT_SEARCH, name='{}%'.format(search))
    else:
        buffer = execute_query(SELECT_PROJECT)

    # Return the notebook list
    project_list = []

    for project in buffer:
        project_list.append({'id': project[0], 'name': project[1], 'description': project[2]})

    return project_list


def insert_project(name, description=None):
    """ Create a new project

    :param name: Project name
    :type name: str
    :param description: Project description
    :type description: str
    :return: ID of the inserted row
    """
    return execute_query_last_insert_rowid(INSERT_PROJECT, name=name, description=description)


def update_project(proj_id, name, description):
    """ Update project information for the specified ID

    :param proj_id: ID of the project to update
    :type proj_id: int
    :param name: New project name
    :type name: str
    :param description: New project description
    :type description: str
    :return: ID of the inserted row
    """
    return execute_query_last_insert_rowid(UPDATE_PROJECT, proj_id=proj_id, name=name, description=description)


def delete_project(proj_id):
    """ Delete the project with the specified ID

    :param proj_id: ID of the project to delete
    :type proj_id: int
    """
    execute_query(DELETE_PROJECT, proj_id=proj_id)


"""
References and related table query
"""


def insert_category(name):
    """ Create a new category

    :param name: Category name
    :type name: str
    """
    execute_query(INSERT_CATEGORY, name=name)


def update_category(name, category_id):
    """ Update a category

    :param name: Updated category name
    :type name: str
    :param category_id: ID of the category to update
    :type category_id: int
    """
    execute_query(UPDATE_CATEGORY, name=name, category_id=category_id)


def delete_category(category_id):
    """ Delete a category

    :param category_id: ID of the category to delete
    :type category_id: int
    """
    execute_query(DELETE_CATEGORY, category_id=category_id)


def insert_subcategory(name, category_id):
    """ Create a new reference subcategory

    :param name: Subcategory name
    :type name: str
    :param category_id: Parent category
    :type category_id: int
    """
    execute_query(INSERT_SUBCATEGORY, name=name, category_id=category_id)


def update_subcategory(name, category_id, subcategory_id):
    """ Update a reference subcategory name or category

    :param name: Updated subcategory name
    :type name: str
    :param category_id: Updated subcategory parent category
    :type category_id: int
    :param subcategory_id: ID of the subcategory to update
    :type subcategory_id: int
    """
    execute_query(UPDATE_SUBCATEGORY, name=name, category_id=category_id, subcategory_id=subcategory_id)


def delete_subcategory(subcategory_id):
    """ Delete a reference subcategory

    :param subcategory_id: ID of the subcategory to delete
    :type subcategory_id: int
    """
    execute_query(DELETE_SUBCATEGORY, subcategory_id=subcategory_id)


def select_category():
    """ Select add the reference categorie """

    buffer = execute_query(SELECT_CATEGORY)

    # Return the category list
    category_list = []

    for category in buffer:
        category_list.append({'id': category[0], 'name': category[1]})

    return category_list


def select_reference_category():
    """ Select all the references """

    # Execute the query
    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    conn.isolation_level = None
    cursor = conn.cursor()

    cursor.execute("BEGIN")
    cursor.execute(SELECT_CATEGORY)
    category_buffer = cursor.fetchall()
    cursor.execute(SELECT_SUBCATEGORY)
    subcategory_buffer = cursor.fetchall()
    cursor.execute(SELECT_REFS)
    reference_buffer = cursor.fetchall()
    cursor.execute("END")
    conn.close()

    # Return the references list
    Category = namedtuple('Category', ['id', 'name', 'subcategory', 'entry'])
    SubCategory = namedtuple('Subcategory', ['id', 'name', 'entry'])
    Reference = namedtuple('Reference', ['uuid', 'title', 'author', 'year'])

    category_list = []

    if category_buffer:
        for category in category_buffer:
            category_id = category[0]
            category_name = category[1]

            subcategory_list = []
            if subcategory_buffer:
                for subcategory in subcategory_buffer:
                    if subcategory[2] == category_id:
                        subcategory_id = subcategory[0]
                        subcategory_name = subcategory[1]

                        reference_list = []
                        if reference_buffer:
                            for reference in reference_buffer:
                                if reference[4] == category_id and reference[5] == subcategory_id:
                                    reference_uuid = data.uuid_string(reference[0])
                                    reference_title = reference[1]
                                    reference_author = reference[2]
                                    reference_year = reference[3]

                                    reference_list.append(Reference(reference_uuid, reference_title,
                                                                    reference_author, reference_year))
                        subcategory_list.append(SubCategory(subcategory_id, subcategory_name, reference_list))

            reference_list = []
            if reference_buffer:
                for reference in reference_buffer:
                    if reference[4] == category_id and reference[5] == None:
                        reference_uuid = data.uuid_string(reference[0])
                        reference_title = reference[1]
                        reference_author = reference[2]
                        reference_year = reference[3]

                        reference_list.append(Reference(reference_uuid, reference_title,
                                                        reference_author, reference_year))
            category_list.append(Category(category_id, category_name, subcategory_list, reference_list))
    return category_list


def insert_ref(ref_uuid, ref_key, ref_type, category_id, subcategory_id=None, file_attached=False, title=None,
               publisher=None, year=None, author=None, editor=None, volume=None, address=None, edition=None,
               journal=None, chapter=None, pages=None, issue=None, description=None, abstract=None, tag_list=None):
    """ Insert a reference """

    # Execute the query
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.isolation_level = None
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # Insert the reference in the database

        cursor.execute("BEGIN")
        cursor.execute(INSERT_REF, {'ref_uuid': ref_uuid,
                                        'ref_key': ref_key,
                                        'ref_type': ref_type,
                                        'file_attached': file_attached,
                                        'title': title,
                                        'publisher': publisher,
                                        'year': year,
                                        'author': author,
                                        'editor': editor,
                                        'volume': volume,
                                        'address': address,
                                        'edition': edition,
                                        'journal': journal,
                                        'chapter': chapter,
                                        'pages': pages,
                                        'issue': issue,
                                        'description': description,
                                        'abstract': abstract,
                                        'subcategory_id': subcategory_id,
                                        'category_id': category_id})

        # Add the tags

        if tag_list:
            for tag in tag_list:
                cursor.execute(INSERT_TAG, {'name': tag})
                cursor.execute(INSERT_TAG_REF, {'ref_uuid': ref_uuid, 'name': tag})

        cursor.execute("COMMIT")


def update_ref(ref_uuid, ref_key, ref_type, title=None, publisher=None, year=None, author=None, editor=None,
               volume=None, address=None, edition=None, journal=None, chapter=None, pages=None, issue=None,
               description=None, abstract=None, tag_list=None):
    """ Update a reference """

    # Execute the query
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.isolation_level = None
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        cursor.execute("BEGIN")

        # Update the reference in the database
        cursor.execute(UPDATE_REF, {'ref_uuid': ref_uuid,
                                    'ref_key': ref_key,
                                    'ref_type': ref_type,
                                    'title': title,
                                    'publisher': publisher,
                                    'year': year,
                                    'author': author,
                                    'editor': editor,
                                    'volume': volume,
                                    'address': address,
                                    'edition': edition,
                                    'journal': journal,
                                    'chapter': chapter,
                                    'pages': pages,
                                    'issue': issue,
                                    'description': description,
                                    'abstract': abstract})

        # Handle the tags
        cursor.execute(SELECT_REFERENCE_TAG_NAME, {'ref_uuid': ref_uuid})
        current_tag_list = cursor.fetchall()

        if tag_list:
            # Create missing tags
            for tag in tag_list:
                if current_tag_list:
                    if tag not in current_tag_list[0]:
                        cursor.execute(INSERT_TAG, {'name': tag})
                        cursor.execute(INSERT_TAG_REF, {'ref_uuid': ref_uuid, 'name': tag})
                else:
                    cursor.execute(INSERT_TAG, {'name': tag})
                    cursor.execute(INSERT_TAG_REF, {'ref_uuid': ref_uuid, 'name': tag})
            # Remove removed tags
            if current_tag_list:
                for tag in current_tag_list[0]:
                    if tag not in tag_list:
                        cursor.execute(DELETE_TAG_REF, {'name': tag, 'ref_uuid': ref_uuid})

                        # Ignore foreign key exception
                        # They are expected to occur if the tag is used elsewhere
                        try:
                            cursor.execute(DELETE_TAG, {'name': tag})
                        except sqlite3.Error as exception:
                            error_code = sqlite_error.sqlite_err_handler(str(exception))
                            if error_code == sqlite_error.FOREIGN_KEY_CODE:
                                pass
                            else:
                                raise
        else:
            if current_tag_list:
                for tag in current_tag_list[0]:
                    cursor.execute(DELETE_TAG_REF, {'name': tag, 'ref_uuid': ref_uuid})

                    # Ignore foreign key exception
                    # They are expected to occur if the tag is used elsewhere
                    try:
                        cursor.execute(DELETE_TAG, {'name': tag})
                    except sqlite3.Error as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))
                        if error_code == sqlite_error.FOREIGN_KEY_CODE:
                            pass
                        else:
                            raise

        cursor.execute("COMMIT")


def select_reference(ref_uuid):
    """ Select data for a specific reference

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    :return: Reference informations
    """

    buffer = execute_query(SELECT_REF, ref_uuid=data.uuid_bytes(ref_uuid))

    # Return the category list
    return {'uuid': data.uuid_string(buffer[0][0]), 'key': buffer[0][1], 'type': buffer[0][2], 'file': buffer[0][3],
            'title': buffer[0][4], 'publisher': buffer[0][5], 'year': buffer[0][6], 'author': buffer[0][7],
            'editor': buffer[0][8], 'volume': buffer[0][9], 'place': buffer[0][10], 'edition': buffer[0][11],
            'journal': buffer[0][12], 'chapter': buffer[0][13], 'pages': buffer[0][14], 'issue': buffer[0][15],
            'description': buffer[0][16], 'abstract': buffer[0][17]}


def update_reference_category(ref_uuid, category_id, subcategory_id=None):
    """ Update reference category and subcategory

    This function is used when the reference is moved by drag and drop in the treeview
    """
    execute_query(UPDATE_REFERENCE_CATEGORY, category_id=category_id, subcategory_id=subcategory_id,
                  ref_uuid=data.uuid_bytes(ref_uuid))


def select_reference_tag_name(ref_uuid):
    """ Select all the tag for a reference

    :param ref_uuid: Reference UUID
    :type ref_uuid: bytes
    :return [str]: List of all tag name for the reference
    """
    buffer = execute_query(SELECT_REFERENCE_TAG_NAME, ref_uuid=ref_uuid)

    tag_list = []

    for tag in buffer:
        tag_list.append(tag[0])
    return tag_list


def select_reference_completer_list():
    """ Get all the dataset key from the database """

    # Execute the query
    buffer = execute_query(SELECT_REFERENCE_COMPLETER_LIST)

    # Return the tag list
    reference_list = []

    for reference in buffer:
        # Prepare the name
        author = None
        label = ""
        if reference[2]:
            author_list = reference[2].split(',')[0]
            if len(author_list) < 2:
                label = "{} & {}".format(author_list[0], author_list[1])
            else:
                label = "{} et al.".format(reference[2].split()[0])
        if reference[3]:
            if label != "":
                label = "{} ({})".format(label, reference[3])
            else:
                label = "({})".format(reference[3])
        if reference[4]:
            if label != "":
                label = "{}, {}".format(label, reference[4])
            else:
                label = "{}".format(reference[4])

        # Create the list
        reference_list.append({'uuid': data.uuid_string(reference[0]), 'key': reference[1], 'name': label})
    return reference_list


"""
Tag query
"""


def select_tag_list():
    """ Get all the tag from the database """

    # Execute the query
    buffer = execute_query(SELECT_TAG)

    # Return the tag list
    tag_list = []

    for tag in buffer:
        tag_list.append(tag[0])

    return tag_list


"""
Sample query
"""


def select_sample(search):
    """ Select all the existing sample id

    :param search: Search string
    :type search: str
    :return: [{}]
    """

    # Execute the query
    if search:
        buffer = execute_query(SELECT_SAMPLE_SEARCH, search='{}%'.format(search))
    else:
        buffer = execute_query(SELECT_SAMPLE)

    # Return the notebook list
    sample_list = []

    for sample in buffer:
        sample_list.append({
            'id': sample[0],
            'custom_id': sample[1],
            'project': sample[2],
            'description': sample[3],
            'treatment_1': sample[4],
            'treatment_2': sample[5],
            'treatment_3': sample[6],
            'treatment_4': sample[7],
            'treatment_5': sample[8],
            'origin': sample[9],
            'location': sample[10],
            'date': sample[11],
            'note': sample[12]
        })

    return sample_list


def create_sample(custom_id=None, project=None, description=None):
    """ Create a new sample in the database

    This function is called when a new incomplete sample is inserted. Only one value should be inserted when using this
    function.
    """
    return execute_query_last_insert_rowid(CREATE_SAMPLE, custom_id=custom_id, description=description, project=project)


def update_sample(spl_id, custom_id=None, description=None, treatment_1=None, treatment_2=None, treatment_3=None,
                  treatment_4=None, treatment_5=None, origin=None, location=None, date=None, note=None, project=None):
    """ Update sample information for the specified ID """
    if custom_id:
        execute_query(UPDATE_SAMPLE_CUSTOM_ID, custom_id=custom_id, spl_id=spl_id)
    elif project:
        execute_query(UPDATE_SAMPLE_PROJECT, project=project, spl_id=spl_id)
    elif description:
        execute_query(UPDATE_SAMPLE_DESCRIPTION, description=description, spl_id=spl_id)
    elif treatment_1:
        execute_query(UPDATE_SAMPLE_TREATMENT_1, treatment_1=treatment_1, spl_id=spl_id)
    elif treatment_2:
        execute_query(UPDATE_SAMPLE_TREATMENT_2, treatment_2=treatment_2, spl_id=spl_id)
    elif treatment_3:
        execute_query(UPDATE_SAMPLE_TREATMENT_3, treatment_3=treatment_3, spl_id=spl_id)
    elif treatment_4:
        execute_query(UPDATE_SAMPLE_TREATMENT_4, treatment_4=treatment_4, spl_id=spl_id)
    elif treatment_5:
        execute_query(UPDATE_SAMPLE_TREATMENT_5, treatment_4=treatment_5, spl_id=spl_id)
    elif origin:
        execute_query(UPDATE_SAMPLE_ORIGIN, origin=origin, spl_id=spl_id)
    elif location:
        execute_query(UPDATE_SAMPLE_LOCATION, location=location, spl_id=spl_id)
    elif date:
        execute_query(UPDATE_SAMPLE_DATE, spl_date=date, spl_id=spl_id)
    elif note:
        execute_query(UPDATE_SAMPLE_NOTE, note=note, spl_id=spl_id)


def delete_sample(spl_id):
    """ Delete the project with the specified ID

    :param spl_id: ID of the sample to delete
    :type spl_id: int
    """
    execute_query(DELETE_SAMPLE, spl_id=spl_id)


def insert_sample(custom_id=None, project=None, description=None, treatment_1=None, treatment_2=None, treatment_3=None,
                  treatment_4=None, treatment_5=None, origin=None, location=None, date=None, note=None):
    """ Insert a sample in the database

    This function is called when a complete sample is inserted.
    """
    execute_query(INSERT_SAMPLE, custom_id=custom_id, project=project, description=description, treatment_1=treatment_1,
                  treatment_2=treatment_2, treatment_3=treatment_3, treatment_4=treatment_4, treatment_5=treatment_5,
                  origin=origin, location=location, spl_date=date, note=note)


"""
Dataset query
"""


def insert_dataset(dt_uuid, name, dt_key, nb_uuid):
    """ Insert a dataset in the database """
    execute_query(INSERT_DATASET, dt_uuid=dt_uuid, name=name, dt_key=dt_key, nb_uuid=nb_uuid)


def update_dataset(dt_uuid, name, dt_key):
    """ Update a dataset in the database """
    execute_query(UPDATE_DATASET, dt_uuid=dt_uuid, name=name, dt_key=dt_key)


def select_dataset():
    """ Select all the notebook """

    # Execute the query
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.isolation_level = None
        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(SELECT_PROJECT)
        project_buffer = cursor.fetchall()
        cursor.execute(SELECT_NOTEBOOK)
        notebook_buffer = cursor.fetchall()
        cursor.execute(SELECT_DATASET)
        dataset_buffer = cursor.fetchall()
        cursor.execute("END")

    # Return the references list
    Project = namedtuple('Project', ['id', 'name', 'notebook'])
    Notebook = namedtuple('Notebook', ['uuid', 'name', 'dataset'])
    Dataset = namedtuple('Dataset', ['uuid', 'name', 'key'])

    project_list = []

    if project_buffer:
        for project in project_buffer:
            project_id = project[0]
            project_name = project[1]

            notebook_list = []
            if notebook_buffer:
                for notebook in notebook_buffer:
                    if notebook[2] == project_id:
                        notebook_uuid = data.uuid_string(notebook[0])
                        notebook_name = notebook[1]

                        dataset_list = []
                        if dataset_buffer:
                            for dataset in dataset_buffer:
                                if data.uuid_string(dataset[3]) == notebook_uuid:
                                    dataset_uuid = data.uuid_string(dataset[0])
                                    dataset_name = dataset[1]
                                    dataset_key = dataset[2]

                                    dataset_list.append(Dataset(dataset_uuid, dataset_name,
                                                                dataset_key))
                        notebook_list.append(Notebook(notebook_uuid, notebook_name, dataset_list))
            project_list.append(Project(project_id, project_name, notebook_list))
    return project_list


def select_dataset_completer_list():
    """ Get all the dataset key from the database """

    # Execute the query
    buffer = execute_query(SELECT_DATASET_COMPLETER_LIST)

    # Return the tag list
    dataset_list = []

    for dataset in buffer:
        dataset_list.append({'uuid': data.uuid_string(dataset[0]), 'key': dataset[1], 'name': dataset[2]})

    return dataset_list

"""
Protocol query
"""


def select_protocol_category():
    """ Select all the protocols """

    # Execute the query
    conn = sqlite3.connect(MAIN_DATABASE_FILE_PATH)
    conn.isolation_level = None
    cursor = conn.cursor()

    cursor.execute("BEGIN")
    cursor.execute(SELECT_CATEGORY)
    category_buffer = cursor.fetchall()
    cursor.execute(SELECT_SUBCATEGORY)
    subcategory_buffer = cursor.fetchall()
    cursor.execute(SELECT_PROTOCOL_LIST)
    protocol_buffer = cursor.fetchall()
    cursor.execute("END")
    conn.close()

    # Return the references list
    Category = namedtuple('Category', ['id', 'name', 'subcategory', 'entry'])
    SubCategory = namedtuple('Subcategory', ['id', 'name', 'entry'])
    Protocol = namedtuple('Protocol', ['uuid', 'title', 'author', 'year'])

    category_list = []

    if category_buffer:
        for category in category_buffer:
            category_id = category[0]
            category_name = category[1]

            subcategory_list = []
            if subcategory_buffer:
                for subcategory in subcategory_buffer:
                    if subcategory[2] == category_id:
                        subcategory_id = subcategory[0]
                        subcategory_name = subcategory[1]

                        protocol_list = []
                        if protocol_buffer:
                            for protocol in protocol_buffer:
                                if protocol[2] == category_id and protocol[3] == subcategory_id:
                                    protocol_uuid = data.uuid_string(protocol[0])
                                    protocol_name = protocol[1]

                                    protocol_list.append(Protocol(protocol_uuid, protocol_name, None, None))
                        subcategory_list.append(SubCategory(subcategory_id, subcategory_name, protocol_list))

            protocol_list = []
            if protocol_buffer:
                for protocol in protocol_buffer:
                    if protocol[2] == category_id and protocol[3] is None:
                        protocol_uuid = data.uuid_string(protocol[0])
                        protocol_name = protocol[1]

                        protocol_list.append(Protocol(protocol_uuid, protocol_name, None, None))
            category_list.append(Category(category_id, category_name, subcategory_list, protocol_list))
    return category_list


def select_protocol_completer_list():
    """ Get all the dataset key from the database """

    # Execute the query
    buffer = execute_query(SELECT_PROTOCOL_COMPLETER_LIST)

    # Return the tag list
    protocol_list = []

    for protocol in buffer:
        protocol_list.append({'uuid': data.uuid_string(protocol[0]), 'key': protocol[1], 'name': protocol[2]})

    return protocol_list


def update_protocol_category(ref_uuid, category_id, subcategory_id=None):
    """ Update protocol category and subcategory

    This function is used when the protocol is moved by drag and drop in the treeview
    """
    execute_query(UPDATE_PROTOCOL_CATEGORY, category_id=category_id, subcategory_id=subcategory_id,
                  ref_uuid=data.uuid_bytes(ref_uuid))



"""
Experiment query
"""


def select_experiment_key_notebook(nb_uuid):
    """ Get all the experiment key for a specific notebook """

    # Execute the query
    buffer = execute_query(SELECT_EXPERIMENT_KEY_NOTEBOOK, nb_uuid=nb_uuid)

    # Return the tag list
    key_list = []

    for key in buffer:
        key_list.append(key[0])

    return key_list


def get_experiment_list_notebook(nb_uuid):
    """ Get all the experiment name and key for a specific notebook """

    # Execute the query
    buffer = execute_query(SELECT_EXPERIMENT_NOTEBOOK, nb_uuid=nb_uuid)

    experiment_list = []

    for experiment in buffer:
        experiment_list.append({'exp_uuid': experiment[0], 'name': experiment[1], 'key': experiment[2]})

    return experiment_list
