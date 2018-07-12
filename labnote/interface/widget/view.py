""" This module contains all the treewidget used in labnote software """

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QTreeView, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItem, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, QSettings

# Project import
from labnote.utils import database
from labnote.core import stylesheet
from labnote.interface.widget.model import StandardItemModel


"""
Tree view
"""


class TreeView(QTreeView):
    """ Base tree view for all labnote subclass """
    def __init__(self):
        super(TreeView, self).__init__()

        # Remove the focus rectangle
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Select single row
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Set edit trigged
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # No tab focus
        self.setFocusPolicy(self.focusPolicy() ^ Qt.TabFocus)

        # Hide the top level header
        self.header().hide()


class DragDropTreeView(QTreeView):
    """ Tree view subclass that handle drag and drop """

    last_index_data = None

    drop_finished = pyqtSignal(QModelIndex)

    def dropEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            event.setDropAction(Qt.IgnoreAction)
            return

        event.acceptProposedAction()
        self.drop_finished.emit(index)
