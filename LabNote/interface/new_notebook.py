"""
This module contains classes that create a new notebook
"""

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtCore import QRegExp

# Project import
from labnote.ui.ui_new_notebook import Ui_NewNotebook
from labnote.utils import database


class NewNotebook(QDialog, Ui_NewNotebook):
    """
    Class that show New Notebook dialog
    """

    def __init__(self):
        super(NewNotebook, self).__init__()
        # Initialize the GUI
        self.setupUi(self)
        self.init_gui()

    def init_gui(self):
        # Set picture
        notebook_image = QPixmap(":/Icons/NewNotebook/icons/new-notebook/1xnotebook.png")
        if self.devicePixelRatio() == 2:
            notebook_image = QPixmap(":/Icons/NewNotebook/icons/new-notebook/2xnotebook.png")
            notebook_image.setDevicePixelRatio(self.devicePixelRatio())

        self.lbl_picture.setPixmap(notebook_image)

        # Set notebook name validator
        validator = QRegExpValidator(QRegExp("^[0-9a-zA-ZÀ-ÿ -._]+$"))
        self.txt_name.setValidator(validator)

        # Instance variable that contain the notebook informations
        self.notebook_name = None
        self.project_id = None

        # Show the project list
        self.show_project_list()

        # Connect slots
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_create.clicked.connect(self.accept)
        self.txt_name.textChanged.connect(self.check_notebook_name)

    def check_notebook_name(self, text):
        if text != "":
            self.btn_create.setEnabled(True)
        else:
            self.btn_create.setEnabled(False)
        self.notebook_name = text
        self.project_id = self.cbx_project.currentData()

    def show_project_list(self):
        """ Get a list of all the projects

        :return: [str] of the projects
        """
        buffer = None

        # Get project list from the database
        try:
            buffer = database.select_project_list()
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the project list")
            message.setInformativeText("An error occurred while getting the project list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Show the notebook list
        self.cbx_project.addItem('', None)
        if buffer:
            for project in buffer:
                self.cbx_project.addItem(project['name'], project['id'])