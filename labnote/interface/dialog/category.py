""" This module contains the library category dialog classes """

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt

# Project import
from labnote.ui.dialog.ui_category import Ui_Category
from labnote.ui.dialog.ui_subcategory import Ui_Subcategory
from labnote.utils import database
from labnote.core import sqlite_error
from labnote.interface.widget.object import NameValidator


class Category(QDialog, Ui_Category):
    """ Class that show the category dialog """

    def __init__(self, name=None, category_id=None):
        super(Category, self).__init__()

        # Global variable definition
        self.category_id = category_id
        self.name = name

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

    def init_ui(self):
        # General properties
        self.setFixedSize(400, 133)

        # Set category name validator
        self.txt_name.setValidator(NameValidator())
        self.txt_name.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Create button
        self.btn_create.setEnabled(False)

        # Show data
        if self.name:
            self.txt_name.setText(self.name)
            self.check_category_name(self.txt_name.text())

    def init_connection(self):
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_create.clicked.connect(self.process)
        self.txt_name.textChanged.connect(self.check_category_name)

    def process(self):
        """ Process the category """
        if not self.category_id:
            try:
                database.insert_category(self.txt_name.text())
            except (sqlite3.Error, OSError) as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.UNIQUE_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Category already exist")
                    message.setInformativeText("Category name must be unique. Please choose a different name")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                else:
                    message = QMessageBox(QMessageBox.Warning, "Error creating the category",
                                          "An error occurred during the category creation.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                return
        else:
            try:
                database.update_category(self.txt_name.text(), self.category_id)
            except (sqlite3.Error, OSError) as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.UNIQUE_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Category already exist")
                    message.setInformativeText("Category name must be unique. Please choose a different name")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                else:
                    message = QMessageBox(QMessageBox.Warning, "Error updating the category",
                                          "An error occurred while updating the category.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                return
        self.accept()

    def check_category_name(self, text):
        """ Enable the create button if the category name is not empty """
        if text != "":
            self.btn_create.setEnabled(True)
        else:
            self.btn_create.setEnabled(False)


class Subcategory(QDialog, Ui_Subcategory):
    """ Class that show the subcategory dialog """

    def __init__(self, name=None, subcategory_id=None):
        super(Subcategory, self).__init__()

        # Global variable definition
        self.subcategory_id = subcategory_id
        self.name = name

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

    def init_ui(self):
        # General properties
        self.setFixedSize(400, 169)

        # Set category name validator
        self.txt_name.setValidator(NameValidator())
        self.txt_name.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Create button
        self.btn_create.setEnabled(False)

        # Show the category list
        self.show_category_list()

        # Show data
        if self.name:
            self.txt_name.setText(self.name)
            self.check_subcategory_name(self.txt_name.text())

    def init_connection(self):
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_create.clicked.connect(self.process)
        self.txt_name.textChanged.connect(self.check_subcategory_name)

    def show_category_list(self):
        """ Get a list of all the category """

        buffer = None

        # Get project list from the database
        try:
            buffer = database.select_category()
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the category list")
            message.setInformativeText("An error occurred while getting the category list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Show the notebook list
        if buffer:
            for category in buffer:
                self.cbx_category.addItem(category['name'], category['id'])

    def process(self):
        """ Process the category """
        if not self.subcategory_id:
            try:
                database.insert_subcategory(self.txt_name.text(), self.cbx_category.currentData())
            except (sqlite3.Error, OSError) as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.UNIQUE_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Category already exist")
                    message.setInformativeText("Category name must be unique. Please choose a different name")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                else:
                    message = QMessageBox(QMessageBox.Warning, "Error creating the category",
                                          "An error occurred during the category creation.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                return
        else:
            try:
                database.update_subcategory(self.txt_name.text(), self.cbx_category.currentData(),
                                                self.subcategory_id)
            except (sqlite3.Error, OSError) as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.UNIQUE_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Subcategory already exist")
                    message.setInformativeText("Subcategory name must be unique. Please choose a different name")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                else:
                    message = QMessageBox(QMessageBox.Warning, "Error updating the subcategory",
                                          "An error occurred while updating the subcategory.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                return
        self.accept()

    def check_subcategory_name(self, text):
        """ Enable the create button if the category name is not empty """
        if text != "":
            self.btn_create.setEnabled(True)
        else:
            self.btn_create.setEnabled(False)
