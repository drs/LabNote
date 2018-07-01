""" This module returns SQLite errors code depending on the error string received

This module is required because sqlite3 does not return the error number and only the error string.
"""

# Python import
import sqlite3

FOREIGN_KEY_STR = "FOREIGN KEY constraint failed"
FOREIGN_KEY_CODE = 787
NOT_NULL_STR = "NOT NULL constraint failed"
NOT_NULL_CODE = 1299
PRIMARY_STR = "PRIMARY KEY constraint failed"
PRIMARY_CODE = 1555
UNIQUE_STR = "UNIQUE constraint failed"
UNIQUE_CODE = 2067


def sqlite_err_handler(err_string):
    """

    :param err_string: SQLite error string
    :type err_string: str
    :return: The error number associated with the string
    """
    if FOREIGN_KEY_STR in err_string:
        return FOREIGN_KEY_CODE
    elif NOT_NULL_STR in err_string:
        return NOT_NULL_CODE
    elif PRIMARY_STR in err_string:
        return PRIMARY_CODE
    elif UNIQUE_STR in err_string:
        return UNIQUE_CODE
    else:
        return -1
