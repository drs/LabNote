# Python import
import os

# Project import
from data_management import database, directory
from common import logs


def check_folder_integrity():
    """ Check is the main directory exist.

    If it does not create the main directory and the required databases.
    If it exist continue checking it's integrity.
    """
    if not os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH):
        # Create the main directory
        directory.create_default_main_directory()
        logs.init_logging() # Start logging when the main directory is created

        # Create the general database
        database.create_main_database()
        database.create_protocol_db()
    else:
        logs.init_logging() # Start logging
