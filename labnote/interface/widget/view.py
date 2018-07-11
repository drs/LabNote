""" This module contains all the treewidget used in labnote software """

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QTreeView, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItem, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex

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


class ProjectNotebookTreeView(TreeView):
    """ This class manage the data in the project and notebook tree widget

    This class is defined because the exact same widget in used in mainwindow and dataset
    """

    # Define global constant
    QT_LevelRole = Qt.UserRole + 1

    LEVEL_PROJECT = 101
    LEVEL_NOTEBOOK = 102

    def __init__(self):
        super(ProjectNotebookTreeView, self).__init__()
        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/view/project_notebook_tree_view.qss")

        self.show_content()

    def show_content(self):
        """ Show the notebook and project in the tree widget """
        reference_list = None

        try:
            notebook_list = database.select_notebook_project()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the notebook data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        model = StandardItemModel()
        root = model.invisibleRootItem()

        if notebook_list:
            for project in notebook_list:
                project_item = QStandardItem(project.name)
                project_item.setData(project.id, Qt.UserRole)
                project_item.setData(self.LEVEL_PROJECT, self.QT_LevelRole)
                project_item.setFont(QFont(self.font().family(), 12, QFont.Bold))
                root.appendRow(project_item)

                if project.notebook:
                    for notebook in project.notebook:
                        notebook_item = QStandardItem(notebook.name)
                        notebook_item.setData(notebook.uuid, Qt.UserRole)
                        notebook_item.setData(self.LEVEL_NOTEBOOK, self.QT_LevelRole)
                        project_item.appendRow(notebook_item)

        self.setModel(model)