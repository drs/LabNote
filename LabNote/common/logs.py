# Python import
import os
import datetime
import logging

DEFAULT_MAIN_DIRECTORY_PATH = os.path.expanduser("~/Documents/LabNote")
LOG_DIRECTORY_PATH = os.path.join(DEFAULT_MAIN_DIRECTORY_PATH + "/logs")
LOG_FILE = os.path.join(LOG_DIRECTORY_PATH + "/{}_labnote.log".format(datetime.datetime.now().strftime("%Y-%m-%d")))


def init_logging():
    """ Initialise login

    .. note::
        This fonction is required in this module only because this is the module reponsible for the creation of
        the file structure that normally contains the logs.
    """

    # Initialise the log file if the file structure exists
    if os.path.isdir(LOG_DIRECTORY_PATH):
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO)