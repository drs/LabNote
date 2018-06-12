""" This module contains the functions required to create and edit experiment binary files """

# Python import
import os

# Project import
from LabNote.data_management import directory


def encode_experiment(html):
    """ Encode experiment data to binary

    :param html: HTLM string to encode to binary
    :type html: str
    :return: Encoded HTML string
    """
    return html.encode()


def create_experiment(exp_uuid, nb_uuid, data):
    """ Create a notebook with data

    :param exp_uuid: Experiment uuid
    :type exp_uuid: UUID
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :param data: Notebook data
    :type data: bytearray
    """
    notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))
    experiment_file_path = os.path.join(experiment_path + "/{}".format(exp_uuid))

    experiment_file = None

    try:
        experiment_file = open(experiment_file_path, "wb")
        experiment_file.write(data)
    except OSError as exception:
        return exception
    except IOError as exception:
        return exception
    finally:
        if experiment_file:
            experiment_file.close()


def read_experiment(exp_uuid, nb_uuid):
    """

    :param exp_uuid:
    :param nb_uuid:
    :return:
    """
    notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))
    experiment_file_path = os.path.join(experiment_path + "/{}".format(exp_uuid))

    experiment_file = None
    html = None

    try:
        experiment_file = open(experiment_file_path, "rb")
        data = experiment_file.read()
        html = data.decode()
        return html
    except OSError as exception:
        return exception
    except IOError as exception:
        return exception
    finally:
        if experiment_file:
            experiment_file.close()