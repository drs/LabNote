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


class ProjectNotebookTreeView(TreeView):
    """ This class manage the data in the project and notebook tree widget

    This class is defined because the exact same widget in used in mainwindow and dataset
    """

    # Define global constant
    QT_LevelRole = Qt.UserRole + 1

    LEVEL_PROJECT = 101
    LEVEL_NOTEBOOK = 102

    # Signal definition
    selection_changed = pyqtSignal(int, str)

    def __init__(self):
        super(ProjectNotebookTreeView, self).__init__()
        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/view/project_notebook_tree_view.qss")

        self.show_content()

        self.collapsed.connect(self.save_state)
        self.expanded.connect(self.save_state)

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
        self.selectionModel().currentChanged.connect(self.selection_change)
        self.restore_state()

    def get_hierarchy_level(self, index):
        """ Get the hierarchy level for the index

        :param index: Item index
        :type index: QModelIndex
        :return int: Hierarchy level
        """
        if index.data(self.QT_LevelRole) == self.LEVEL_PROJECT:
            return 1
        elif index.data(self.QT_LevelRole) == self.LEVEL_NOTEBOOK:
            return 2

    def selection_change(self):
        """ Emit the selection changed signal """

        index = self.selectionModel().currentIndex()
        hierarchy_level = self.get_hierarchy_level(index)

        self.selection_changed.emit(hierarchy_level, str(index.data(Qt.UserRole)))

    def current_selection(self):
        """ Return the current selected item data in display and user role """
        index = self.selectionModel().currentIndex()
        return [index.data(Qt.UserRole), index.data(Qt.DisplayRole)]

    def get_project(self, index):
        """ Return a category id

        :param index: Item index
        :type index: QModelIndex
        :return int: Category id
        """
        hierarchy_level = self.get_hierarchy_level(index)

        if hierarchy_level == 1:
            return index.data(Qt.UserRole)
        elif hierarchy_level == 2:
            return index.parent().data(Qt.UserRole)
        else:
            return None

    def save_state(self):
        """ Save the treeview expanded state """

        # Generate list
        expanded_item = []
        for index in self.model().get_persistant_index_list():
            if self.isExpanded(index) and index.data(Qt.UserRole):
                expanded_item.append(index.data(Qt.UserRole))

        # Save list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("NotebookProjectTreeView")
        settings.setValue("ExpandedItem", expanded_item)
        settings.endGroup()

    def restore_state(self):
        """ Restore the treeview expended state """

        # Get list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("NotebookProjectTreeView")
        expanded_item = settings.value("ExpandedItem")
        selected_item = settings.value("SelectedItem")
        settings.endGroup()

        model = self.model()

        if expanded_item:
            for item in expanded_item:
                match = model.match(model.index(0, 0), Qt.UserRole, item, 1, Qt.MatchRecursive)

                if match:
                    self.setExpanded(match[0], True)

