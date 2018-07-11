"""
This module contain the classes responsible for launching and managing the project dialog.
"""

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import QEvent, Qt

# Project import
from labnote.ui.ui_project import Ui_Project
from labnote.utils import database
from labnote.core import sqlite_error, stylesheet
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.interface.widget.tablewidgetitem import NoEditTableWidgetItem


class Project(QDialog, Ui_Project):
    """
    Class responsible of managing the project window interface.
    """

    # Class variable initialization
    current_text = None
    row = -1
    column = -1
    old_row = -1
    old_column = -1
    old_text = None

    def __init__(self, parent=None):
        super(Project, self).__init__(parent)
        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Show the project list
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
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Search text edit
        self.txt_search = SearchLineEdit()
        self.layout_title.insertWidget(3, self.txt_search)

        # Install event filter
        self.table.setMouseTracking(True)
        self.table.installEventFilter(self)
        self.table.viewport().installEventFilter(self)

    def init_connection(self):
        self.btn_close.clicked.connect(self.close)
        self.txt_search.textChanged.connect(self.show_project_list)
        self.table.currentCellChanged.connect(self.cell_changed)
        self.table.cellEntered.connect(self.set_cursor_position)

    def eventFilter(self, widget, event):
        if widget == self.table.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if not self.table.itemAt(event.pos()):
                    self.no_cell_selected()
        if widget == self.table:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Backspace:
                    self.delete_project()
        return QDialog().eventFilter(widget, event)

    def no_cell_selected(self):
        """ Check if the sample must be saved """
        if not (self.column == -1 or self.row == -1):
            if self.current_text is not None and not self.table.item(self.row, self.column).text() == self.current_text:
                if not self.save_change(self.row, self.column):
                    self.table.editItem(self.table.item(self.row, self.column))
            self.current_text = None
            self.old_column = -1
            self.old_row = -1
            self.old_text = None
            self.row = -1
            self.column = -1

    def cell_changed(self):
        # Stop the execution if no cell was selected before since there is nothing to save
        # in this case
        if not self.table.item(self.old_row, self.old_column):
            return

        # Save the current cell text
        if self.old_text is not None and not self.table.item(self.old_row, self.old_column).text() == self.old_text:
            if not self.save_change(self.old_row, self.old_column):
                self.table.editItem(self.table.item(self.old_row, self.old_column))

    def set_cursor_position(self, row, column):
        """ Set the current and past cursor position as global variable

        :param row: Row of the cell entered by the cursor
        :type row: int
        :param column: Column of the cell entered by the cursor
        :type column: int
        """
        self.old_column = self.column
        self.old_row = self.row
        self.old_text = self.current_text
        self.column = column
        self.row = row
        self.current_text = self.table.item(row, column).text()

    def show_project_list(self):
        """ Show the list of all existing project """
        project_list = []
        search = (self.txt_search.text() or None)

        try:
            project_list = database.select_project_list(search)
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the project list")
            message.setInformativeText("An unhandled error occurred while getting the project list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Prepare the table
        self.table.clear()
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Project name'))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem('Description'))

        # Add existing project
        if project_list:
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

        # Add empty row at the end
        if not search:
            self.add_empty_row()

    def add_empty_row(self):
        """ Create a last empty row """
        # Add the row
        self.table.setRowCount(self.table.rowCount()+1)
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount()-1, 2, NoEditTableWidgetItem())

    def save_change(self, row, column):
        """ Save changes in the database

        :param row: Row that changed
        :type row: int
        """
        id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        description = self.table.item(row, 2).text()

        # Save changes in database
        try:
            if row + 1 == self.table.rowCount() and not self.table.item(row, column).text() == "":
                inserted_id = database.create_project(name, description)
                self.table.item(row, 0).setText(str(inserted_id))
                self.table.item(row, 2).setFlags(self.table.item(row, 2).flags() | Qt.ItemIsEditable)
                self.add_empty_row()
            elif not row + 1 == self.table.rowCount() and not self.table.item(row, column).text() == "":
                database.update_project(id, name, description)
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

                self.table.item(row, column).setText(self.current_text)
                return False
            elif error_code == sqlite_error.NOT_NULL_CODE:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Error while editing a project")
                message.setInformativeText("Project must have a name.")
                message.setIcon(QMessageBox.Information)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()

                self.table.item(row, column).setText(self.current_text)
                return False
            else:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Error while editing a project")
                message.setInformativeText("An unhandeled error occured while editing a project.")
                message.setDetailedText(str(exception))
                message.setIcon(QMessageBox.Warning)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()
        return True

    def delete_project(self):
        """ Delete project """
        try:
            selection = self.table.selectedRanges()
            if len(selection) == 1:
                delete_row = selection[0].topRow()
                for row in range(selection[0].topRow(), selection[0].bottomRow()+1):
                    proj_id = self.table.item(delete_row, 0).text()
                    database.delete_project(proj_id=proj_id)
                    self.table.removeRow(delete_row)
            else:
                row = self.table.currentRow()
                proj_id = self.table.item(row, 0).text()
                database.delete_project(proj_id=proj_id)
                self.table.removeRow(row)
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unable to delete project")
            message.setInformativeText("An unhandeled error occured while deleting project.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
            return
