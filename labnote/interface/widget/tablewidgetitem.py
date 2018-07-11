""" This module contains all the QTableWidgetItem subclass used in the software """

# PyQt import
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt


class NoEditTableWidgetItem(QTableWidgetItem):
    def __init__(self):
        super(NoEditTableWidgetItem, self).__init__()
        self.setFlags(self.flags() ^ Qt.ItemIsEditable)
        self.setText('')
