""" This module contains the dataset dialog class """

# Python import
import sqlite3
import uuid

# PyQt import
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

# Project import
from labnote.ui.dialog.ui_dataset import Ui_Dataset
from labnote.utils import database, fsentry
from labnote.core import sqlite_error, data
from labnote.interface.widget.object import NameValidator, KeyValidator


class DatasetDialog(QDialog, Ui_Dataset):
    """ Class that show the dataset dialog """

    def __init__(self, dt_uuid=None, name=None, key=None, nb_uuid=None):
        super(DatasetDialog, self).__init__()

        # Class variable definition
        self.dt_uuid = dt_uuid
        self.name = name
        self.key = key
        self.nb_uuid = nb_uuid

        # Signal definition
        closed = pyqtSignal()

        self.setupUi(self)
        self.init_ui()
        self.init_connection()

    def init_ui(self):
        # General properties
        self.setFixedSize(400, 202)

        # Set validator
        self.txt_name.setValidator(NameValidator())

        self.txt_key.setValidator(KeyValidator())

        # Set lineedit properties
        self.txt_name.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.txt_key.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Create button
        self.btn_create.setEnabled(False)

        # Show data
        if self.name:
            self.txt_name.setText(self.name)
            self.check_fields()
        if self.key:
            self.txt_key.setText(self.key)
            self.check_fields()
        if self.dt_uuid:
            self.cbx_notebook.setEnabled(False)
            self.btn_create.setText("Update")
        self.show_notebook_list()

    def init_connection(self):
        self.btn_cancel.clicked.connect(self.reject)
        self.txt_name.textChanged.connect(self.check_fields)
        self.txt_key.textChanged.connect(self.check_fields)
        self.btn_create.clicked.connect(self.process)

    def check_fields(self):
        """ Check if the key and name exist to enable the create button """
        if self.txt_name.text() != "" and self.txt_key.text() != "":
            self.btn_create.setEnabled(True)
        else:
            self.btn_create.setEnabled(False)

    def process(self):
        """ Process the dataset in the database """
        if not self.dt_uuid:
            try:
                fsentry.create_dataset(str(uuid.uuid4()), self.txt_name.text(), self.txt_key.text(),
                                       self.cbx_notebook.currentData(Qt.UserRole))
            except (sqlite3.Error, OSError) as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.UNIQUE_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Dataset already exist")
                    message.setInformativeText("Dataset key must be unique within a notebook. "
                                               "Please choose a different key.")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                    return
                else:
                    message = QMessageBox(QMessageBox.Warning, "Cannot create dataset",
                                          "An error occurred during the dataset creation.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                    return
        else:
            try:
                database.update_dataset(data.uuid_bytes(self.dt_uuid), self.txt_name.text(),
                                        self.txt_key.text())
            except (sqlite3.Error, OSError) as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.UNIQUE_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Dataset already exist")
                    message.setInformativeText("Dataset key must be unique within a notebook. "
                                               "Please choose a different key.")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                    return
                else:
                    message = QMessageBox(QMessageBox.Warning, "Cannot update dataset",
                                          "An error occurred while updating the dataset.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                    return
        self.accept()

    def show_notebook_list(self):
        """ Show the notebook list in the combobox """
        notebook_list = None

        # Get project list from the database
        try:
            notebook_list = database.select_notebook_project()
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the project list")
            message.setInformativeText("An error occurred while getting the project list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
            return

        # Show the notebook list
        if notebook_list:
            for project in notebook_list:
                if project.notebook:
                    for notebook in project.notebook:
                        self.cbx_notebook.addItem("{} - {}".format(project.name, notebook.name), notebook.uuid)
