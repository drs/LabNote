""" This module contains the file system integrity check for the LabNote file system """

# Python import
import os
import sqlite3
import logging
from io import StringIO

# Project import
from labnote.utils import database, directory, fsentry

FATAL_ERROR = 1
ERROR = 2
WARNING = 3


class IntegrityCheck:
    """ This class is responsible of check the LabNote file system integrity """
    def __init__(self):
        self.notebook_list = []

        # Start logging to a string
        self.log_stream = StringIO()
        format = '%(asctime)s :: %(levelname)s :: %(message)s'
        logging.basicConfig(stream=self.log_stream, level=logging.INFO, format=format)

    def full_check(self):
        """ Check the full file system integrity

        :return: If an error occured [str, int] that contains the log and error level
        """
        # If an error occured send it to caller
        if not self._check_main_directory():
            return [self.log_stream.getvalue(), FATAL_ERROR]
        return []

    @staticmethod
    def _check_main_directory():
        """ Check the main directory integrity """

        logging.info('Checking main directory integrity...')

        # Check if the main directory exists
        if not os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH):
            logging.info('The main directory does not exist...')

            try:
                logging.info('Creating the main directory...')
                fsentry.create_main_directory()
            except OSError as exception:
                logging.fatal('An error occured while creating the main directory...')
                logging.exception(exception)
                try:
                    logging.info('Cleaning up the main directory...')
                    fsentry.cleanup_main_directory()
                except OSError as exception:
                    logging.fatal('An error occured while cleaning up the main directory')
                    logging.exception(exception)
                    logging.fatal('Main directory integrity :: FAILED')
                    return False
                logging.fatal('Main directory integrity :: FAILED')
                return False
            logging.info('The main directory was created...')
        # Check if the default subdirectories and files exists
        elif not (os.path.isdir(directory.NOTEBOOK_DIRECTORY_PATH) and
                  os.path.isfile(database.MAIN_DATABASE_FILE_PATH) and
                  os.path.isfile(database.PROTOCOL_DATABASE_FILE_PATH)):
            logging.info('The main directory is corrupted...')

            try:
                fsentry.cleanup_main_directory()
                fsentry.create_main_directory()
            except OSError as exception:
                logging.fatal('An error occured while recreating the main directory')
                logging.exception(exception)
                logging.fatal('Main directory integrity :: FAILED')
                return False
        # Check if it is possible to connect with the databases
        else:
            logging.info('Checking main directory database connectivity...')
            try:
                sqlite3.connect(database.MAIN_DATABASE_FILE_PATH)
                sqlite3.connect(database.PROTOCOL_DATABASE_FILE_PATH)
            except sqlite3.Error as exception:
                logging.fatal('An error occured while connecting with the database...')
                logging.exception(str(exception))
                return False
        logging.info('Main directory integrity :: OK')
        return True

    def _check_notebook(self):
        """ Check that all notebook in the main database exists """

        # Set return value to true
        # This variable is changed to false if any error occurs
        ret = True

        logging.info('Checking notebook integrity...')

        # Check if directories for notebooks in database exists
        logging.info('Checking if notebook in database have a directory integrity...')

        db_notebook_list = database.get_notebook_list()
        for notebook in db_notebook_list:
            logging.info('Checking notebook {} ...'.format(notebook['name']))
            notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(notebook['uuid']))
            if not os.path.isdir(notebook_path):
                logging.info('There is no directory for notebook {} ...'.format(notebook['name']))
                try:
                    logging.info('Deleting notebook {} database entry...'.format(notebook['name']))
                    database.delete_notebook(notebook['uuid'])
                except sqlite3.Error:
                    logging.warning('An error occured while deleting the notebook {} in the database...'
                                    .format(notebook['name']))
                    logging.exception(sqlite3.Error)
                    ret = False
            else:
                self.notebook_list.append(notebook['uuid'])

        # Check if directories have an existing notebook in the database
        logging.info('Checking if notebook directory have a database field...')

        dir_notebook_list = os.listdir(directory.NOTEBOOK_DIRECTORY_PATH)

        for notebook in dir_notebook_list:
            logging.info('Checking notebook directory {} ...'.format(notebook))

            if not notebook in self.notebook_list:
                logging.info('There is no database entry for notebook {} ...'.format(notebook))
                try:
                    logging.info('Deleting directory for notebook {} ...'.format(notebook))
                    directory.delete_nb_directory(notebook)
                except OSError as exception:
                    logging.warning('An error occured while deleting the directory for notebook {}...'
                                    .format(notebook))
                    logging.exception(sqlite3.Error)
                    ret = False

        if ret:
            logging.info('Notebook filesystem integrity :: OK')
            return True
        else:
            logging.warning('Notebook filesystem integrity :: FAILED')
            return False
