"""
This module contain the classes responsible for launching and managing the project dialog.
"""

# Python import
import sqlite3

# PyQt import
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import Qt

# Project import
from labnote.ui.ui_project import Ui_Project
from labnote.utils import database
from labnote.core import sqlite_error, stylesheet


class Project(QDialog, Ui_Project):
    """
    Class responsible of managing the project window interface.
    """
    def __init__(self, parent=None):
        super(Project, self).__init__(parent)

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()

        # Add the project list
        self.show_project_list()

        # Show the dialog
        self.show()

    def init_ui(self):
        self.setWindowTitle("LabNote - Project")

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/project.qss")

        # Table
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.setShowGrid(False)

        # Search text edit
        search_icon = QIcon(":/Icons/MainWindow/icons/main-window/search.png")
        self.txt_search.addAction(search_icon, QLineEdit.LeadingPosition)
        self.txt_search.setFixedWidth(250)
        self.txt_search.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Connect slots
        self.btn_close.clicked.connect(self.close)
        self.table.cellChanged.connect(self.save_change)
        self.txt_search.textChanged.connect(self.show_project_list)

    def show_project_list(self):
        """ Show the list of all existing project """

        # Block all signals for the table
        self.table.blockSignals(True)

        project_list = None
        search = (self.txt_search.text() or None)

        try:
            project_list = database.select_project_list(search)
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the project list")
            message.setInformativeText("An error occurred while getting the project list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        if project_list:
            # Prepare the table
            self.table.clear()
            self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Project name'))
            self.table.setHorizontalHeaderItem(2, QTableWidgetItem('Description'))
            self.table.setRowCount(len(project_list))

            # Add items to the list
            row = 0
            for project in project_list:
                id = QTableWidgetItem(str(project['id']))
                name = QTableWidgetItem(project['name'])
                description = QTableWidgetItem(project['description'])
                self.table.setItem(row, 0, id)
                self.table.setItem(row, 1, name)
                self.table.setItem(row, 2, description)

                row = row + 1

            # Order the list
            self.table.sortItems(1, Qt.AscendingOrder)
            self.table.setCurrentCell(0, 0)

            if not search:
                self.add_empty_row()

        # Unblock all signal for the table
        self.blockSignals(False)

    def add_empty_row(self):
        """ Create a last empty row """
        # Block all signals for the table
        self.table.blockSignals(True)

        # Add the row
        self.table.setRowCount(self.table.rowCount()+1)
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount()-1, 2, QTableWidgetItem(''))

        # Unblock all signals for the table
        self.table.blockSignals(False)

    def save_change(self, row):
        """ Save changes in the database

        :param row: Row that changed
        :type row: int
        """
        inserted_id = None
        id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        description = self.table.item(row, 2).text()

        # Save changes in database
        try:
            if row + 1 == self.table.rowCount():
                inserted_id = database.create_project(name, description)
            else:
                inserted_id = database.update_project(id, name, description)
        except sqlite3.Error as exception:
            error_code = sqlite_error.sqlite_err_handler(str(exception))

            if error_code == sqlite_error.UNIQUE_CODE:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Error while editing a project")
                message.setInformativeText("Project name must be unique. Please choose a different name")
                message.setIcon(QMessageBox.Information)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()
            elif error_code == sqlite_error.NOT_NULL_CODE:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Error while editing a project")
                message.setInformativeText("Project must have a name.")
                message.setIcon(QMessageBox.Information)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()
            else:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Error while editing a project")
                message.setInformativeText("An unhandeled error occured while editing a project.")
                message.setDetailedText(str(exception))
                message.setIcon(QMessageBox.Warning)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()

        # Update the newly inserted item id
        if not id:
            if inserted_id:
                # Block all signals for the table
                self.table.blockSignals(True)

                self.table.item(row, 0).setText(str(inserted_id))

                # Unblock all signals for the table
                self.table.blockSignals(False)
            self.add_empty_row()
