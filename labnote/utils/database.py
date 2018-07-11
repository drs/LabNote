# Python import
import sqlite3
import os
from collections import namedtuple

# Project import
from labnote.utils import directory
from labnote.utils.conversion import uuid_bytes, uuid_string
from labnote.core import data

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
    proj_id INTEGER       REFERENCES project (proj_id)  ON DELETE RESTRICT,
    UNIQUE (name, proj_id)
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

CREATE_REF_CATEGORY_TABLE = """
CREATE TABLE ref_category (
    category_id INTEGER       PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR (255) UNIQUE
                              NOT NULL
)
"""

CREATE_REF_SUBCATEGORY_TABLE = """
CREATE TABLE ref_subcategory (
    subcategory_id INTEGER       PRIMARY KEY AUTOINCREMENT,
    name           VARCHAR (255) NOT NULL,
    category_id    INTEGER       REFERENCES ref_category (category_id) ON DELETE RESTRICT
                                 NOT NULL,
    UNIQUE (name, category_id)
)
"""

CREATE_REFS_TABLE = """
CREATE TABLE refs (
    ref_uuid       BLOB (16)     PRIMARY KEY,
    ref_key        VARCHAR (255) NOT NULL       UNIQUE,
    ref_type       INTEGER       NOT NULL,
    file_attached  BOOLEAN       NOT NULL       DEFAULT FALSE,
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
    subcategory_id INTEGER       REFERENCES ref_subcategory (subcategory_id) ON DELETE RESTRICT,
    category_id    INTEGER       REFERENCES ref_subcategory (subcategory_id) ON DELETE RESTRICT
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
SELECT nb_uuid, name, proj_id FROM notebook ORDER BY name ASC
"""

INSERT_NOTEBOOK = """
INSERT INTO notebook (nb_uuid, name, proj_id) VALUES (:nb_uuid, :name, :proj_id)
"""

INSERT_EXPERIMENT = """
INSERT INTO experiment (exp_uuid, nb_uuid, name, objective) 
VALUES (:exp_uuid, :nb_uuid, :name, :objective)
"""

SELECT_NOTEBOOK_EXPERIMENT = """
SELECT exp_uuid, name, objective FROM experiment WHERE nb_uuid = :nb_uuid
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

SELECT_EXPERIMENT = """
SELECT name, objective FROM experiment WHERE exp_uuid = :exp_uuid
"""

UPDATE_EXPERIMENT = """
UPDATE experiment SET name = :name, objective = :objective WHERE  exp_uuid = :exp_uuid
"""

DELETE_EXPERIMENT = """
DELETE FROM experiment WHERE exp_uuid = :exp_uuid
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

INSERT_REF_CATEGORY = """
INSERT INTO ref_category (name) VALUES (:name)
"""

UPDATE_REF_CATEGORY = """
UPDATE ref_category SET name = :name WHERE category_id = :category_id
"""

DELETE_REF_CATEGORY = """
DELETE FROM ref_category WHERE category_id = :category_id
"""

INSERT_REF_SUBCATEGORY = """
INSERT INTO ref_subcategory (name, category_id) VALUES (:name, :category_id)
"""

UPDATE_REF_SUBCATEGORY = """
UPDATE ref_subcategory SET name = :name, category_id = :category_id WHERE subcategory_id = :subcategory_id
"""

DELETE_REF_SUBCATEGORY = """
DELETE FROM ref_subcategory WHERE subcategory_id = :subcategory_id
"""

SELECT_REF_CATEGORY = """
SELECT category_id, name FROM ref_category ORDER BY name ASC
"""

SELECT_REF_SUBCATEGORY = """
SELECT subcategory_id, name, category_id FROM ref_subcategory ORDER BY category_id ASC, name ASC
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

DELETE_TAG = """
DELETE FROM tags WHERE name = :name
"""

DELETE_TAG_REF = """
DELETE FROM refs_tag WHERE tag_id = (SELECT tag_id FROM tags WHERE name = :name)
"""

SELECT_TAG = """
SELECT name FROM tags
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
    cursor.execute(CREATE_REF_CATEGORY_TABLE)
    cursor.execute(CREATE_REF_SUBCATEGORY_TABLE)
    cursor.execute(CREATE_REFS_TABLE)
    cursor.execute(CREATE_SAMPLE_TABLE)
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


def insert_ref_category(name):
    """ Create a reference new category

    :param name: Category name
    :type name: str
    """
    execute_query(INSERT_REF_CATEGORY, name=name)


def update_ref_category(name, category_id):
    """ Update a reference category name

    :param name: Updated category name
    :type name: str
    :param category_id: ID of the category to update
    :type category_id: int
    """
    execute_query(UPDATE_REF_CATEGORY, name=name, category_id=category_id)


def delete_ref_category(category_id):
    """ Delete a reference category

    :param category_id: ID of the category to delete
    :type category_id: int
    """
    execute_query(DELETE_REF_CATEGORY, category_id=category_id)


def insert_ref_subcategory(name, category_id):
    """ Create a new reference subcategory

    :param name: Subcategory name
    :type name: str
    :param category_id: Parent category
    :type category_id: int
    """
    execute_query(INSERT_REF_SUBCATEGORY, name=name, category_id=category_id)


def update_ref_subcategory(name, category_id, subcategory_id):
    """ Update a reference subcategory name or category

    :param name: Updated subcategory name
    :type name: str
    :param category_id: Updated subcategory parent category
    :type category_id: int
    :param subcategory_id: ID of the subcategory to update
    :type subcategory_id: int
    """
    execute_query(UPDATE_REF_SUBCATEGORY, name=name, category_id=category_id, subcategory_id=subcategory_id)


def delete_ref_subcategory(subcategory_id):
    """ Delete a reference subcategory

    :param subcategory_id: ID of the subcategory to delete
    :type subcategory_id: int
    """
    execute_query(DELETE_REF_SUBCATEGORY, subcategory_id=subcategory_id)


def select_ref_category():
    """ Select add the reference categorie """

    buffer = execute_query(SELECT_REF_CATEGORY)

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
    cursor.execute(SELECT_REF_CATEGORY)
    category_buffer = cursor.fetchall()
    cursor.execute(SELECT_REF_SUBCATEGORY)
    subcategory_buffer = cursor.fetchall()
    cursor.execute(SELECT_REFS)
    reference_buffer = cursor.fetchall()
    cursor.execute("END")
    conn.close()

    # Return the references list
    Category = namedtuple('Category', ['id', 'name', 'subcategory', 'reference'])
    SubCategory = namedtuple('Subcategory', ['id', 'name', 'reference'])
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
               journal=None, chapter=None, pages=None, issue=None, description=None, abstract=None):
    """ Insert a reference """
    execute_query(INSERT_REF, ref_uuid=ref_uuid, ref_key=ref_key, ref_type=ref_type, file_attached=file_attached,
                  title=title, publisher=publisher, year=year, author=author, editor=editor, volume=volume,
                  address=address, edition=edition, journal=journal, chapter=chapter, pages=pages, issue=issue,
                  description=description, abstract=abstract, subcategory_id=subcategory_id, category_id=category_id)


def update_ref(ref_uuid, ref_key, ref_type, title=None, publisher=None, year=None, author=None, editor=None,
               volume=None, address=None, edition=None, journal=None, chapter=None, pages=None, issue=None,
               description=None, abstract=None):
    """ Update a reference """
    execute_query(UPDATE_REF, ref_key=ref_key, ref_type=ref_type, title=title, publisher=publisher, year=year,
                  author=author, editor=editor, volume=volume, address=address, edition=edition, journal=journal,
                  chapter=chapter, pages=pages, issue=issue, description=description, abstract=abstract,
                  ref_uuid=data.uuid_bytes(ref_uuid))


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


def delete_reference(ref_uuid):
    """ Delete a reference from the database

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    """
    execute_query(DELETE_REF, ref_uuid=data.uuid_bytes(ref_uuid))


def update_reference_category(ref_uuid, category_id, subcategory_id=None):
    """ Update reference category and subcategory

    This function is used when the reference is moved by drag and drop in the treeview
    """
    execute_query(UPDATE_REFERENCE_CATEGORY, category_id=category_id, subcategory_id=subcategory_id,
                  ref_uuid=data.uuid_bytes(ref_uuid))


def insert_tag_ref(ref_uuid, name):
    """ Insert the reference tag

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    :param name: Tag name
    :type name: str
    """

    # Execute the query
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.isolation_level = None
        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(INSERT_TAG, {'name': name})
        cursor.execute(INSERT_TAG_REF, {'ref_uuid': ref_uuid, 'name': name})
        cursor.execute("END")


def delete_tag_ref(name):
    """ Insert the reference tag

    :param name: Tag name
    :type name: str
    """

    # Execute the query
    with sqlite3.connect(MAIN_DATABASE_FILE_PATH) as conn:
        conn.isolation_level = None
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute("BEGIN")
        cursor.execute(DELETE_TAG_REF, {'name': name})
        cursor.execute(DELETE_TAG, {'name': name})
        cursor.execute("END")


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
        tag_list.append({'name': tag[0]})

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
