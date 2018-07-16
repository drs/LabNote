""" This module contains all the functions used to handle files """

# Python import
import os
import shutil
import uuid

# Project import
from labnote.utils import directory


def copy_file_to_data(nb_uuid, exp_uuid, path):
    """ Move a file to an experiment data folder

    :param nb_uuid: UUID of the notebook that contains the experiment
    :type nb_uuid: str
    :param exp_uuid: Experiment UUID
    :type exp_uuid: str
    :param path: Path of the file to copy
    :param path: str
    """

    notebook_path = os.path.join(directory.NOTEBOOK_DIRECTORY_PATH + "/{}".format(nb_uuid))
    experiment_path = os.path.join(notebook_path + "/{}".format(exp_uuid))
    data_path = os.path.join(experiment_path + "/data")

    file_uuid = uuid.uuid4()

    data_file = os.path.join(data_path + "/{}".format(file_uuid))

    try:
        shutil.copy2(path, data_file)
    except OSError as exception:
        return exception


def protocol_image_path(prt_uuid, extension):
    """ Return the protocol image path

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Protocol image path
    """
    return os.path.join(directory.protocol_resource_path(prt_uuid=prt_uuid) + "/{}.{}".format(str(uuid.uuid4()), extension))


def add_image_protocol(prt_uuid, path, extention):
    """ Add an image to a protocol resources

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Path of the inserted image
    """
    image_path = protocol_image_path(prt_uuid, extention)
    shutil.copy2(path, image_path)
    return image_path


def copy_dataset(dt_uuid, nb_uuid, path):
    """ Copy a dataset """
    file_name = dataset_excel_file(dt_uuid=dt_uuid, nb_uuid=nb_uuid)
    shutil.copy2(path, file_name)


def reference_file_path(ref_uuid):
    """ Return the path to a reference file

    :param ref_uuid: Reference UUID
    :type ref_uuid: str
    """
    return os.path.join(directory.REFERENCES_DIRECTORY_PATH + "/{}.pdf".format(ref_uuid))


def dataset_excel_file(dt_uuid, nb_uuid):
    """ Return a dataset file path

    :param dt_uuid: Dataset UUID
    :type dt_uuid: str
    :param nb_uuid: Notebook UUID
    :type nb_uuid: str
    """
    return os.path.join(directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid) + "/{}.xlsx".format(dt_uuid))


def protocol_file(prt_uuid):
    """ Return the path to a protocol file in the file system

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Protocol file path
    """
    return os.path.join(directory.protocol_path(prt_uuid=prt_uuid) + "/{}.labnp".format(prt_uuid))


def experiment_file(nb_uuid, exp_uuid):
    """ Return the path to a experiment file in the file system

    :param nb_uuid: Notebook uuid
    :type nb_uuid: str
    :param exp_uuid: Experiment uuid
    :type exp_uuid: str
    :return str: Experiment file path
    """
    return os.path.join(directory.experiment_path(nb_uuid, exp_uuid) + "/{}.labnp".format(exp_uuid))


def experiment_image_path(nb_uuid, exp_uuid, extension):
    """ Return the protocol image path

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Protocol image path
    """
    return os.path.join(directory.experiment_resource_path(nb_uuid=nb_uuid, exp_uuid=exp_uuid) +
                        "/{}.{}".format(str(uuid.uuid4()), extension))


def add_image_experiment(nb_uuid, exp_uuid, path, extention):
    """ Add an image to a protocol resources

    :param prt_uuid: Protocol uuid
    :type prt_uuid: str
    :return str: Path of the inserted image
    """
    image_path = experiment_image_path(nb_uuid=nb_uuid, exp_uuid=exp_uuid, extension=extention)
    shutil.copy2(path, image_path)
    return image_path


def dataset_r_file(nb_uuid, dt_uuid):
    """ Return the dataset r file path

    :param dt_uuid: Dataset uuid
    :type dt_uuid: str
    :return: Path r file
    """
    return os.path.join(directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid) + "/{}.R".format(dt_uuid))


def dataset_r_notebook_file(nb_uuid, dt_uuid):
    """ Return the dataset r file path

    :param dt_uuid: Dataset uuid
    :type dt_uuid: str
    :return: Path r file
    """
    return os.path.join(directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid) + "/{}.Rmd".format(dt_uuid))


def dataset_python_file(nb_uuid, dt_uuid):
    """ Return the dataset python file path

    :param dt_uuid: Dataset uuid
    :type dt_uuid: str
    :return: Path python file
    """
    return os.path.join(directory.dataset_path(nb_uuid=nb_uuid, dt_uuid=dt_uuid) + "/{}.py".format(dt_uuid))

