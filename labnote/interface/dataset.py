""" This module contains the classes that show the dataset dialog """

# Python import
import sqlite3
import xlrd
import os
import subprocess

# PyQt import
from PyQt5.QtWidgets import QDialog, QMessageBox, QMenu, QAction, QFileDialog, QTabWidget, QTableWidget, \
    QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import QSize, Qt, QSettings, QDir, pyqtSignal, QItemSelectionModel
from PyQt5.QtGui import QIcon, QStandardItem, QFont

# Project import
from labnote.ui.ui_dataset import Ui_Dataset
from labnote.core import stylesheet
from labnote.utils import database, fsentry, files, layout
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.interface.dialog import dataset
from labnote.interface.widget.model import StandardItemModel
from labnote.interface.widget.view import TreeView
from labnote.interface.widget.widget import NoEntryWidget


# Constant definition

# Data type
QT_LevelRole = Qt.UserRole+1
QT_KeyRole = QT_LevelRole+1

# Level type
LEVEL_PROJECT = 101
LEVEL_NOTEBOOK = 102
LEVEL_DATASET = 103


class Dataset(QDialog, Ui_Dataset):
    """ Class responsible of diplaying the dataset window interface """

    # Signals
    closed = pyqtSignal()

    def __init__(self, parent=None, dt_uuid=None):
        super(Dataset, self).__init__(parent)

        # Class variable
        self.contains_file = False

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        if dt_uuid:
            self.show_dataset(dt_uuid)

        # Show the dialog
        self.show()

    def init_ui(self):
        # General properties
        self.setWindowTitle("LabNote - Dataset")
        self.read_settings()

        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/dataset.qss")

        # Setup manage menu
        self.manage_menu = QMenu(self)
        self.manage_menu.setFont(QFont(self.font().family(), 13, QFont.Normal))
        self.act_update_dataset = QAction("Update dataset", self)
        self.act_update_dataset.setEnabled(False)
        self.act_update_dataset.triggered.connect(self.update_dataset)
        self.manage_menu.addAction(self.act_update_dataset)
        self.act_delete_dataset = QAction("Delete dataset", self)
        self.act_delete_dataset.triggered.connect(self.delete_dataset)
        self.act_delete_dataset.setEnabled(False)
        self.manage_menu.addAction(self.act_delete_dataset)
        self.btn_manage.setMenu(self.manage_menu)

        # Setup import button
        self.btn_import.setText("Import")
        icon = QIcon(":/Icon/Sample/icons/sample/import.png")
        icon.addFile(":/Icon/Sample/icons/sample/import_pressed.png", QSize(), QIcon.Normal, QIcon.On)
        self.btn_import.setIcon(icon)
        self.btn_import.setCheckable(True)
        self.btn_import.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_import.setEnabled(False)

        # Setup open in excel button
        self.btn_open.setText("Open in Excel")
        self.btn_open.setIcon(QIcon(":/Icon/Dataset/icons/dataset/excel.png"))
        self.btn_open.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_open.setEnabled(False)

        # Setup R button
        self.btn_r.setText("R Script")
        self.btn_r.setIcon(QIcon(":/Icon/Dataset/icons/dataset/r.png"))
        self.btn_r.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_r.setEnabled(False)

        # Setup R run button
        self.btn_r_run.setText("Run R Script")
        self.btn_r_run.setIcon(QIcon(":/Icon/Dataset/icons/dataset/r_run.png"))
        self.btn_r_run.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_r_run.setEnabled(False)

        # Setup python button
        self.btn_python.setText("Python")
        self.btn_python.setIcon(QIcon(":/Icon/Dataset/icons/dataset/python.png"))
        self.btn_python.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_python.setEnabled(False)

        # Setup python run button
        self.btn_python_run.setText("Run Python")
        self.btn_python_run.setIcon(QIcon(":/Icon/Dataset/icons/dataset/python_run.png"))
        self.btn_python_run.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_python_run.setEnabled(False)

        # Search lineedit
        self.txt_search = SearchLineEdit()
        self.layout_search.insertWidget(17, self.txt_search)

        # Setup treeview
        self.view_dataset = TreeView()
        self.frame_tree.layout().insertWidget(0, self.view_dataset)
        self.view_dataset.setFixedWidth(240)

        # Show the entry widget
        self.layout_entry.addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)

        # Show content
        self.show_dataset_list()

    def init_connection(self):
        self.btn_close.clicked.connect(self.close)
        self.btn_add.clicked.connect(self.create_dataset)
        self.view_dataset.collapsed.connect(self.save_treeview_state)
        self.view_dataset.expanded.connect(self.save_treeview_state)
        self.btn_import.clicked.connect(self.import_dataset)
        self.btn_open.clicked.connect(self.open_dataset)

    def show_dataset(self, dt_uuid):
        """ Show the dataset with the given uuid

        :param dt_uuid: Dataset uuid
        :type dt_uuid: str
        """
        model = self.view_dataset.model()
        match = model.match(model.index(0, 0), Qt.UserRole, dt_uuid, 1, Qt.MatchRecursive)
        if match:
            self.view_dataset.selectionModel().setCurrentIndex(match[0], QItemSelectionModel.Select)
            self.view_dataset.repaint()

    def create_dataset(self):
        """ Create a new dataset """
        self.dataset_dialog = dataset.DatasetDialog()
        self.dataset_dialog.setWindowModality(Qt.WindowModal)
        self.dataset_dialog.setParent(self, Qt.Sheet)
        self.dataset_dialog.show()
        self.dataset_dialog.accepted.connect(self.show_dataset_list)

    def update_dataset(self):
        """ Update a dataset informations """
        index = self.view_dataset.selectionModel().currentIndex()
        dt_uuid = index.data(Qt.UserRole)
        name = index.data(Qt.DisplayRole)
        key = index.data(QT_KeyRole)
        nb_uuid = self.get_notebook(index)

        self.dataset_dialog = dataset.DatasetDialog(dt_uuid=dt_uuid, name=name, key=key, nb_uuid=nb_uuid)
        self.dataset_dialog.setWindowModality(Qt.WindowModal)
        self.dataset_dialog.setParent(self, Qt.Sheet)
        self.dataset_dialog.show()
        self.dataset_dialog.accepted.connect(self.show_dataset_list)

    def delete_dataset(self):
        index = self.view_dataset.selectionModel().currentIndex()
        dt_uuid = index.data(Qt.UserRole)
        nb_uuid = self.get_notebook(index)

        try:
            fsentry.delete_dataset(dt_uuid=dt_uuid, nb_uuid=nb_uuid)
        except (sqlite3.Error, OSError) as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while deleting dataset",
                                  "An error occurred while deleting the dataset list.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return
        self.show_dataset_list()

    def import_dataset(self):
        """ Import the dataset """
        self.btn_import.setChecked(True)
        dialog = QFileDialog()
        file_name = dialog.getOpenFileName(self, "Import Excel Spreadsheet", QDir().homePath(), "Excel Files (*.xlsx)")
        self.btn_import.setChecked(False)

        if file_name[0]:
            index = self.view_dataset.selectionModel().currentIndex()
            dt_uuid = index.data(Qt.UserRole)
            nb_uuid = self.get_notebook(index)

            try:
                files.copy_dataset(dt_uuid=dt_uuid, nb_uuid=nb_uuid, path=file_name[0])
            except OSError as exception:
                message = QMessageBox(QMessageBox.Warning, "Error while copying dataset",
                                      "An error occurred while copying the dataset Excel sheet.", QMessageBox.Ok)
                message.setWindowTitle("LabNote")
                message.setDetailedText(str(exception))
                message.exec()
                return

            layout.empty_layout(self, self.layout_entry)
            self.show_dataset(index)

    def open_dataset(self):
        """ Open the dataset in excel """
        index = self.view_dataset.selectionModel().currentIndex()
        dt_uuid = index.data(Qt.UserRole)
        nb_uuid = self.get_notebook(index)

        subprocess.check_call(['open', '-a', 'Microsoft Excel', files.dataset_excel_file(dt_uuid=dt_uuid,
                                                                                         nb_uuid=nb_uuid)])

    def show_dataset_list(self):
        """ Show the dataset list in the tree view """
        dataset_list = None

        try:
            dataset_list = database.select_dataset()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading dataset",
                                  "An error occurred while loading the dataset list.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        model = StandardItemModel()
        root = model.invisibleRootItem()

        if dataset_list:
            for project in dataset_list:
                project_item = QStandardItem(project.name)
                project_item.setData(project.id, Qt.UserRole)
                project_item.setData(LEVEL_PROJECT, QT_LevelRole)
                project_item.setFont(QFont(self.font().family(), 12, QFont.Bold))
                root.appendRow(project_item)

                if project.notebook:
                    for notebook in project.notebook:
                        notebook_item = QStandardItem(notebook.name)
                        notebook_item.setData(notebook.uuid, Qt.UserRole)
                        notebook_item.setData(LEVEL_NOTEBOOK, QT_LevelRole)
                        project_item.appendRow(notebook_item)

                        if notebook.dataset:
                            for dataset in notebook.dataset:
                                dataset_item = QStandardItem(dataset.name)
                                dataset_item.setData(dataset.uuid, Qt.UserRole)
                                dataset_item.setData(LEVEL_DATASET, QT_LevelRole)
                                dataset_item.setData(dataset.key, QT_KeyRole)
                                notebook_item.appendRow(dataset_item)

        self.view_dataset.setModel(model)
        self.view_dataset.selectionModel().currentChanged.connect(self.selection_changed)
        self.restore_treeview_state()

    def selection_changed(self):
        """ Update the interface according to the selected item in the tree """

        layout.empty_layout(self, self.layout_entry)

        index = self.view_dataset.selectionModel().currentIndex()
        hierarchy_level = self.get_hierarchy_level(index)

        if hierarchy_level == 1 or hierarchy_level == 2:
            self.act_delete_dataset.setEnabled(False)
            self.act_update_dataset.setEnabled(False)
            self.btn_import.setEnabled(False)
            self.btn_open.setEnabled(False)
            self.btn_r.setEnabled(False)
            self.btn_r_run.setEnabled(False)
            self.btn_python.setEnabled(False)
            self.btn_python_run.setEnabled(False)
            self.layout_entry.addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)
            self.contains_file = False
        elif hierarchy_level == 3:
            self.act_delete_dataset.setEnabled(True)
            self.act_update_dataset.setEnabled(True)
            self.show_dataset(index)
            if not self.contains_file:
                self.btn_import.setEnabled(True)
                self.btn_open.setEnabled(False)
                self.btn_r.setEnabled(False)
                self.btn_r_run.setEnabled(False)
                self.btn_python.setEnabled(False)
                self.btn_python_run.setEnabled(False)
            else:
                self.btn_import.setEnabled(False)
                self.btn_open.setEnabled(True)
                self.btn_r.setEnabled(True)
                self.btn_r_run.setEnabled(True)
                self.btn_python.setEnabled(True)
                self.btn_python_run.setEnabled(True)

    def show_dataset(self, index):
        """ Show the dataset content """

        dt_uuid = index.data(Qt.UserRole)
        nb_uuid = self.get_notebook(index)

        excel_file_path = files.dataset_excel_file(dt_uuid=dt_uuid, nb_uuid=nb_uuid)

        if os.path.isfile(excel_file_path):
            book = xlrd.open_workbook(excel_file_path)

            sheets = book.sheet_names()

            tab_widget = QTabWidget()
            tab_widget.setTabPosition(QTabWidget.South)

            for sheet_name in sheets:
                sheet = book.sheet_by_name(sheet_name)
                table_widget = QTableWidget()

                table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
                table_widget.setSelectionMode(QAbstractItemView.NoSelection)
                table_widget.setRowCount(sheet.nrows-1)
                table_widget.setColumnCount(sheet.ncols)
                tab_widget.addTab(table_widget, sheet.name)

                for row in range(0, sheet.nrows):
                    for column in range(0, sheet.ncols):
                        cell = sheet.cell(row, column)
                        if row == 0:
                            table_widget.setHorizontalHeaderItem(column, QTableWidgetItem(cell.value))
                        else:
                            table_widget.setItem(row-1, column, QTableWidgetItem(cell.value))

                table_widget.resizeColumnsToContents()
                table_widget.horizontalHeader().setStretchLastSection(True)

            self.contains_file = True
            self.layout_entry.addWidget(tab_widget)
        else:
            self.contains_file = False
            self.layout_entry.addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)

    def get_hierarchy_level(self, index):
        """ Get the hierarchy level for the index

        :param index: Item index
        :type index: QModelIndex
        :return int: Hierarchy level
        """
        if index.data(QT_LevelRole) == LEVEL_PROJECT:
            return 1
        elif index.data(QT_LevelRole) == LEVEL_NOTEBOOK:
            return 2
        elif index.data(QT_LevelRole) == LEVEL_DATASET:
            return 3

    def get_notebook(self, index):
        """ Return the notebook uuid for the item at index

        :param index: Item index
        :type index: QModelIndex
        :return str: Notebook uuid
        """
        hierarchy_level = self.get_hierarchy_level(index)

        if hierarchy_level == 2:
            return index.data(Qt.UserRole)
        elif hierarchy_level == 3:
            return index.parent().data(Qt.UserRole)
        else:
            return None

    def closeEvent(self, event):
        self.save_treeview_state()
        self.save_settings()
        self.closed.emit()
        event.accept()

    def save_settings(self):
        """ Save the dialog geometry """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Dataset")
        settings.setValue("Geometry", self.saveGeometry())
        settings.setValue("Maximized", self.isMaximized())
        settings.endGroup()

    def read_settings(self):
        """ Restore the dialog geometry """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Dataset")
        self.restoreGeometry(settings.value("Geometry", self.saveGeometry()))
        if settings.value("Maximized", self.isMaximized()):
            self.showMaximized()
        settings.endGroup()

    def save_treeview_state(self):
        """ Save the treeview expanded state """

        # Generate list
        expanded_item = []
        for index in self.view_dataset.model().get_persistant_index_list():
            if self.view_dataset.isExpanded(index) and index.data(Qt.UserRole):
                expanded_item.append(index.data(Qt.UserRole))

        # Save list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Dataset")
        settings.setValue("ExpandedItem", expanded_item)
        settings.endGroup()

    def restore_treeview_state(self):
        """ Restore the treeview expended state """

        # Get list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Dataset")
        expanded_item = settings.value("ExpandedItem")
        selected_item = settings.value("SelectedItem")
        settings.endGroup()

        model = self.view_dataset.model()

        if expanded_item:
            for item in expanded_item:
                match = model.match(model.index(0, 0), Qt.UserRole, item, 1, Qt.MatchRecursive)

                if match:
                    self.view_dataset.setExpanded(match[0], True)
