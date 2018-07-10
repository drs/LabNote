"""
This module contains the class used in the sample number dialog
"""

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QEvent

# Project import
from labnote.ui.ui_sample import Ui_Sample
from labnote.core import stylesheet, data
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.utils import database


class Sample(QDialog, Ui_Sample):

    # Class variable initialization
    current_text = None
    row = -1
    column = -1
    old_row = -1
    old_column = -1

    def __init__(self, parent=None):
        super(Sample, self).__init__(parent)
        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Show the sample list
        self.show_sample_list()

        # Show the dialog
        self.show()

    def init_ui(self):
        self.setWindowTitle("LabNote - Sample")

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/sample.qss")

        # Add search lineedit
        self.txt_search = SearchLineEdit()
        self.layout_title.insertWidget(3, self.txt_search)

        # Setup table
        self.table.setColumnCount(12)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(150)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)

        self.table.setMouseTracking(True)
        self.table.installEventFilter(self)
        self.table.viewport().installEventFilter(self)

    def init_connection(self):
        self.btn_close.clicked.connect(self.close)
        self.txt_search.textChanged.connect(self.show_sample_list)
        self.table.currentCellChanged.connect(self.cell_changed)
        self.table.cellEntered.connect(self.set_cursor_position)

    def eventFilter(self, object, event):
        if object == self.table.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if not self.table.itemAt(event.pos()):
                    self.no_cell_selected()
        if object == self.table:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Backspace:
                    self.delete_sample()
        return QDialog().eventFilter(object, event)

    def no_cell_selected(self):
        """ Check if the sample must be saved """

        if not (self.column == -1 or self.row == -1):
            if self.current_text is not None and not self.table.item(self.row, self.column).text() == self.current_text:
                if not self.save_change(self.row, self.column):
                    self.table.editItem(self.table.item(self.row, self.column))
            self.current_text = None

    def cell_changed(self, row, column, old_row, old_column):
        """ Save the current cell text """
        # Stop the execution if no cell was selected before since there is nothing to save
        # in this case
        if not self.table.item(old_row, old_column):
            return

        if not (column == -1 or row == -1):
            if self.current_text is not None and not self.table.item(old_row, old_column).text() == self.current_text:
                if not self.save_change(old_row, old_column):
                    self.table.editItem(self.table.item(old_row, old_column))
            self.current_text = self.table.item(row, column).text()

    def set_cursor_position(self, row, column):
        """ Set the current and past cursor position as global variable

        :param row: Row of the cell entered by the cursor
        :type row: int
        :param column: Column of the cell entered by the cursor
        :type column: int
        """
        self.old_column = self.column
        self.old_row = self.row
        self.column = column
        self.row = row

    def delete_sample(self):
        """ Delete a sample """
        try:
            selection = self.table.selectedRanges()
            if len(selection) == 1:
                delete_row = selection[0].topRow()
                for row in range(selection[0].topRow(), selection[0].bottomRow()+1):
                    spl_id = self.table.item(delete_row, 0).text()
                    database.delete_sample(spl_id=spl_id)
                    self.table.removeRow(delete_row)
            else:
                row = self.table.currentRow()
                spl_id = self.table.item(row, 0).text()
                database.delete_sample(spl_id=spl_id)
                self.table.removeRow(row)
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unable to delete samples")
            message.setInformativeText("An unhandeled error occured while deleting samples.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
            return

    def show_sample_list(self):
        """ Show the list off all existing samples """
        sample_list = []
        search = (self.txt_search.text() or None)

        try:
            sample_list = database.select_sample(search)
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unable to get the sample list")
            message.setInformativeText("An unhandled error occurred while getting the sample list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        # Prepare the table
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('Sample number'))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Custom number'))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem('Description'))
        self.table.setHorizontalHeaderItem(3, QTableWidgetItem('Origin'))
        self.table.setHorizontalHeaderItem(4, QTableWidgetItem('Treatment 1'))
        self.table.setHorizontalHeaderItem(5, QTableWidgetItem('Treatment 2'))
        self.table.setHorizontalHeaderItem(6, QTableWidgetItem('Treatment 3'))
        self.table.setHorizontalHeaderItem(7, QTableWidgetItem('Treatment 4'))
        self.table.setHorizontalHeaderItem(8, QTableWidgetItem('Treatment 5'))
        self.table.setHorizontalHeaderItem(9, QTableWidgetItem('Location'))
        self.table.setHorizontalHeaderItem(10, QTableWidgetItem('Date'))
        self.table.setHorizontalHeaderItem(11, QTableWidgetItem('Note'))

        # Add existing sample
        if sample_list:
            self.table.setRowCount(len(sample_list))

            # Add items to the list
            row = 0
            for sample in sample_list:
                id = QTableWidgetItem(str(sample['id']))
                id.setFlags(id.flags() ^ Qt.ItemIsEditable)
                custom_id = QTableWidgetItem(sample['custom_id'])
                description = QTableWidgetItem(sample['description'])
                treatment_1 = QTableWidgetItem(sample['treatment_1'])
                treatment_2 = QTableWidgetItem(sample['treatment_2'])
                treatment_3 = QTableWidgetItem(sample['treatment_3'])
                treatment_4 = QTableWidgetItem(sample['treatment_4'])
                treatment_5 = QTableWidgetItem(sample['treatment_5'])
                origin = QTableWidgetItem(sample['origin'])
                location = QTableWidgetItem(sample['location'])
                date = QTableWidgetItem(sample['date'])
                note = QTableWidgetItem(sample['note'])

                self.table.setItem(row, 0, id)
                self.table.setItem(row, 1, custom_id)
                self.table.setItem(row, 2, description)
                self.table.setItem(row, 3, origin)
                self.table.setItem(row, 4, treatment_1)
                self.table.setItem(row, 5, treatment_2)
                self.table.setItem(row, 6, treatment_3)
                self.table.setItem(row, 7, treatment_4)
                self.table.setItem(row, 8, treatment_5)
                self.table.setItem(row, 9, location)
                self.table.setItem(row, 10, date)
                self.table.setItem(row, 11, note)

                row = row + 1

        # Add empty row at the end
        if not search:
            self.add_empty_row()

    def add_empty_row(self):
        """ Create a last empty row """
        # Add the row
        self.table.setRowCount(self.table.rowCount() + 1)
        id = QTableWidgetItem('')
        id.setFlags(id.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(self.table.rowCount() - 1, 0, id)
        self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 2, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 3, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 4, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 5, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 6, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 7, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 8, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 9, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 10, QTableWidgetItem(''))
        self.table.setItem(self.table.rowCount() - 1, 11, QTableWidgetItem(''))

    def save_change(self, row, column):
        """ Save changes in the database

        :param row: Row that changed
        :type row: int
        """
        id = self.table.item(row, 0).text()
        custom_id = data.prepare_string(self.table.item(row, 1).text())
        description = data.prepare_string(self.table.item(row, 2).text())
        origin = data.prepare_string(self.table.item(row, 3).text())
        treatment_1 = data.prepare_string(self.table.item(row, 4).text())
        treatment_2 = data.prepare_string(self.table.item(row, 5).text())
        treatment_3 = data.prepare_string(self.table.item(row, 6).text())
        treatment_4 = data.prepare_string(self.table.item(row, 7).text())
        treatment_5 = data.prepare_string(self.table.item(row, 8).text())
        location = data.prepare_string(self.table.item(row, 9).text())
        date = data.prepare_string(self.table.item(row, 10).text())
        note = data.prepare_string(self.table.item(row, 11).text())

        # Save changes in database
        try:
            if row + 1 == self.table.rowCount() and (1 <= column <= 6) \
                    and not self.table.item(row, column).text() == "":
                inserted_id = database.create_sample(custom_id=custom_id, description=description,
                                                     treatment_1=treatment_1, treatment_2=treatment_2,
                                                     treatment_3=treatment_3, origin=origin)
                self.table.item(row, 0).setText(str(inserted_id))
                self.add_empty_row()
            elif not row + 1 == self.table.rowCount() and not self.table.item(row, column).text() == "":
                if column == 1:
                    database.update_sample(spl_id=id, custom_id=custom_id)
                elif column == 2:
                    database.update_sample(spl_id=id, description=description)
                elif column == 3:
                    database.update_sample(spl_id=id, origin=origin)
                elif column == 4:
                    database.update_sample(spl_id=id, treatment_1=treatment_1)
                elif column == 5:
                    database.update_sample(spl_id=id, treatment_2=treatment_2)
                elif column == 6:
                    database.update_sample(spl_id=id, treatment_3=treatment_3)
                elif column == 7:
                    database.update_sample(spl_id=id, treatment_4=treatment_4)
                elif column == 8:
                    database.update_sample(spl_id=id, treatment_5=treatment_5)
                elif column == 9:
                    database.update_sample(spl_id=id, location=location)
                elif column == 10:
                    database.update_sample(spl_id=id, date=date)
                elif column == 11:
                    database.update_sample(spl_id=id, note=note)
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unable to edit a sample")
            message.setInformativeText("An unhandeled error occured while editing a sample.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
            return False
        return True
