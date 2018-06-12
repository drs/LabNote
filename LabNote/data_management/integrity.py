# Python import
import os

# PyQt import
from PyQt5.QtWidgets import QMessageBox

# Project import
from LabNote.data_management import database, directory

NO_EXCEPTION = -1
MAIN_DIRECTORY_CREATION_EXCEPTION = 0
MAIN_DATABASE_CREATION_EXCEPTION = 1
PROTOCOLS_DATABASE_CREATION_EXCEPTION = 2


def check_folder_integrity():
    """ Check is the main directory exist.

    If it does not create the main directory and the required databases.
    If it exist continue checking it's integrity.

    :returns: Exception with it's exception code[int, Exception]
        -1 - No exception
        0 - Main directory creation exception
        1 - Main database creation exception
        2 - Protocols database creation exception
    """
    # Check if the main directory exists
    if not os.path.isdir(directory.DEFAULT_MAIN_DIRECTORY_PATH):
        # Create the main directory
        create_default_main_directory_exception = directory.create_default_main_directory()
        if create_default_main_directory_exception:
            return [MAIN_DIRECTORY_CREATION_EXCEPTION, create_default_main_directory_exception]
        else:
            # Create the general database
            create_main_database_exception = database.create_main_database()
            if create_main_database_exception:
                return [MAIN_DATABASE_CREATION_EXCEPTION, create_main_database_exception]
            else:
                create_protocol_db_exception = database.create_protocol_db()
                if create_protocol_db_exception:
                    return [PROTOCOLS_DATABASE_CREATION_EXCEPTION, create_protocol_db_exception]
            return [NO_EXCEPTION, "No exception"]
    else:
        return [NO_EXCEPTION, "No exception"]
