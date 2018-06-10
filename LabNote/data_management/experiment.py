""" This module contains the functions required to create and edit experiment binary files """

# Python import
import os
import logging

# Project import
from LabNote.data_management import directory


def create_empty_experiment(exp_uuid, nb_uuid):
    """ Create an empty notebook

    :param exp_uuid: Experiment uuid
    :type exp_uuid: UUID
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    """
    notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))
    experiment_file_path = os.path.join(experiment_path + "/{}".format(exp_uuid))

    experiment_file = None
    data = bytearray()

    try:
        experiment_file = open(experiment_file_path, "wb")
        experiment_file.write(data)
    except OSError as exception:
        # Log the exception
        logging.warning("An exception occured while creating a file for the experiment ({})".format(exp_uuid))
        logging.exception(str(exception))

        return exception
    except IOError as exception:
        # Log the exception
        logging.info("An exception occured while creating a file for the experiment ({})".format(exp_uuid))
        logging.exception(str(exception))

        return exception
    finally:
        if experiment_file:
            experiment_file.close()

