""" This module contains the functions required to create and edit experiment binary files """

# Python import
import os

# Project import
from LabNote.data_management import directory, database
from LabNote.common import common


def create_experiment(exp_uuid, nb_uuid, body, name, objective):
    """ Create a new experiment

    This function is responsible of adding the experiment to the database and to create all the required
    directories

    :param exp_uuid: Experiment uuid
    :type exp_uuid: UUID
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :param body: Experiment body HTML
    :type body: str
    :param name: Experiment name
    :type name: str
    :param objective: Experiment objective
    :type objective: str
    :returns: Exception if an exception occurs
    """
    create_experiment_exception = directory.create_exp_directory(exp_uuid, nb_uuid)
    if not create_experiment_exception:
        create_experiment_database_exception = database.create_experiment(name, exp_uuid, objective, nb_uuid)
        if not create_experiment_database_exception:
            write_experiment_exception = write_experiment(exp_uuid, nb_uuid, encode_experiment(body))
            if not write_experiment_exception:
                return None
            else:
                return write_experiment_exception
        else:
            return create_experiment_database_exception
    else:
        return create_experiment_exception


def encode_experiment(html):
    """ Encode experiment data to binary

    :param html: HTLM string to encode to binary
    :type html: str
    :returns: Encoded HTML string
    """
    return html.encode()


def decode_experiment(html):
    """ Decole experiment data to string

    :param html: HTLM binary to decode
    :type html: bytes
    :returns: HTML string
    """
    return html.decode()


def write_experiment(exp_uuid, nb_uuid, data):
    """ Create a notebook with data

    :param exp_uuid: Experiment uuid
    :type exp_uuid: UUID
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :param data: Notebook data
    :type data: bytes
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
    """ Read an experiment file

    :param exp_uuid: Experiment uuid
    :type exp_uuid: UUID
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :returns: HTML string (or exception)
    """
    notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))
    experiment_file_path = os.path.join(experiment_path + "/{}".format(exp_uuid))

    experiment_file = None

    try:
        experiment_file = open(experiment_file_path, "rb")
        data = experiment_file.read()
        html = data.decode()
        return common.ReturnSgl(sgl=html)
    except OSError as exception:
        return common.ReturnSgl(error=exception)
    except IOError as exception:
        return common.ReturnSgl(error=exception)
    finally:
        if experiment_file:
            experiment_file.close()


def open_experiment(exp_uuid, nb_uuid):
    """ Get all the informations about an experiment from the files and the database

    :param exp_uuid: Experiment uuid
    :type exp_uuid: UUID
    :param nb_uuid: Notebook uuid
    :type nb_uuid: UUID
    :returns: HTML string (or exception)
    """
    # Get experiment informations fromt the database
    informations = database.get_experiment_informations(exp_uuid)

    # informations contains a dictionary with the experiment informations
    if informations.dct:
        # Read the experiment body from the experiment file
        body = read_experiment(exp_uuid, nb_uuid)

        # body contains data
        if body.sgl:
            body_string = body.sgl.decode()
            return common.ReturnDict(dct={'name': informations.dct['name'],
                                          'objective': informations.dct['objective'],
                                          'body': body_string})
        # body contains an error
        elif body.error:
            return common.ReturnDict(error=body.error)
    # informations contains an error
    elif informations.error:
        return common.ReturnDict(error=informations.error)
