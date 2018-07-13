""" This module contains the custom widget used in labnote """

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QAction, QMenu, \
    QMessageBox, QAbstractItemView
from PyQt5.QtGui import QPixmap, QFont, QStandardItem, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex

# Project import
from labnote.core import stylesheet
from labnote.interface.widget.view import DragDropTreeView
from labnote.interface.widget.model import StandardItemModel
from labnote.interface.dialog.category import Category, Subcategory
from labnote.utils import database
from labnote.core import sqlite_error, common
from labnote.ui.widget.ui_texteditor import Ui_TextEditor

# Constant definition

# Reference type
TYPE_ARTICLE = common.TYPE_ARTICLE
TYPE_BOOK = common.TYPE_BOOK
TYPE_CHAPTER = common.TYPE_CHAPTER

# Category frame content type
TYPE_LIBRARY = common.TYPE_LIBRARY
TYPE_PROTOCOL = common.TYPE_PROTOCOL

# Data type
QT_LevelRole = common.QT_LevelRole
QT_StateRole = common.QT_StateRole

# Level type
LEVEL_CATEGORY = common.LEVEL_CATEGORY
LEVEL_SUBCATEGORY = common.LEVEL_SUBCATEGORY
LEVEL_ENTRY = common.LEVEL_ENTRY


class NoEntryWidget(QWidget):
    """Widget that indicate that no entry is selected """

    def __init__(self):
        super(NoEntryWidget, self).__init__()
        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/widget/no_entry_widget.qss")

        # Setting up the widget
        no_entry_pixmap = QPixmap(":/Icons/MainWindow/icons/main-window/no_entry_selected.png")
        lbl_no_entry_image = QLabel()
        lbl_no_entry_image.setAlignment(Qt.AlignCenter)

        lbl_no_entry_image.setPixmap(no_entry_pixmap.scaled(16, 16, Qt.KeepAspectRatio))

        lbl_no_entry = QLabel("No entry selected")
        lbl_no_entry.setAlignment(Qt.AlignCenter)

        # Setting up the layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(lbl_no_entry_image)
        main_layout.addWidget(lbl_no_entry)


class CategoryFrame(QWidget):
    """ Class that show and manage the data in the category TreeView """

    # Signal definition
    delete = pyqtSignal(str)  # Delete the entry
    entry_selected = pyqtSignal(str)  # A reference is selected in the treeview
    selection_changed = pyqtSignal()  # Everything except a reference is selected in the treeview
    list_displayed = pyqtSignal()  # The list showed in the treeview

    def __init__(self, title, frame_type):
        super(CategoryFrame, self).__init__()
        self.frame = QFrame()

        # Set style sheet
        self.frame.setStyleSheet("""
        QFrame {
            border-left: none;
            border-top: none;
            border-bottom: none;
            border-right: 0.5px solid rgb(212, 212, 212);
            background-color: rgb(246, 246, 246);
        }
        """)

        # Set class variable
        self.frame_type = frame_type

        # Create the interface
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create the title label
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("""
        QLabel {
            color: rgb(129, 129, 129);
            font: bold 12px;
        }
        """)
        self.layout.addWidget(self.lbl_title)
        self.layout.setSpacing(0)

        # Create the treeview
        self.view_tree = DragDropTreeView()
        self.view_tree.setStyleSheet("""
        QTreeView::item:selected {
            background-color: rgb(216, 216, 216);
            color: black;
        }

        QTreeView::branch:selected {
            background-color: rgb(216, 216, 216);
        }
        
        QTreeView::branch::closed::has-children {
            image: url(:/Icons/Library/icons/library/branch-close.png);
        }

        QTreeView::branch::open::has-children {
            image: url(:/Icons/Library/icons/library/branch-open.png);
        }
        """)
        self.layout.addWidget(self.view_tree)

        # Create the buttons
        self.layout_button = QHBoxLayout()
        self.layout_button.setSpacing(0)
        self.btn_add = QPushButton("+")
        self.btn_add.setStyleSheet("""
        QPushButton {
            /* Border and background color */
            background-color: none;
            border: none;

            /* Text color and font */
            font-family: Al Bayan;
            font: 24pt;
            color: rgb(129, 129, 129);

            /* Button height and width */
            width: 25px;
            min-width: 25px;
            max-height: 25px;

            height: 25px;
            min-height: 25px;
            max-height: 25px;
        }

        QPushButton:pressed {
            /* Border and background color */
            background-color: none;
            border: none;
            color: rgb(72, 72, 72);
        }
        """)
        self.layout_button.addWidget(self.btn_add)
        self.btn_manage = QPushButton()
        self.btn_manage.setStyleSheet("""
        QPushButton {
            border-image: url(:/Icons/MainWindow/icons/main-window/settings.png);
            max-width: 24px;
            min-width: 24px;
            max-height: 16px;
            min-height: 16px;
        }

        QPushButton:pressed {
            border-image: url(:/Icons/MainWindow/icons/main-window/settings_pressed.png);
        }


        QPushButton:pressed {
            /* Border and background color */
            background-color: none;
            border: none;
        }

        QPushButton::menu-indicator {
            height: 0px;
            width: 0px;
        }
        """)
        self.layout_button.addWidget(self.btn_manage)
        self.layout_button.addStretch()
        self.layout.addLayout(self.layout_button)

        self.frame.setLayout(self.layout)

        # Create the manage button menu
        self.manage_menu = QMenu(self)
        self.manage_menu.setFont(QFont(self.font().family(), 13, QFont.Normal))
        self.act_create_category = QAction("Create category", self)
        self.act_create_category.triggered.connect(self.create_category)
        self.manage_menu.addAction(self.act_create_category)
        self.act_update_category = QAction("Update category", self)
        self.act_update_category.triggered.connect(self.update_category)
        self.act_update_category.setEnabled(False)
        self.manage_menu.addAction(self.act_update_category)
        self.act_delete_category = QAction("Delete category", self)
        self.act_delete_category.triggered.connect(self.delete_category)
        self.act_delete_category.setEnabled(False)
        self.manage_menu.addAction(self.act_delete_category)
        self.manage_menu.addSeparator()
        self.act_create_subcategory = QAction("Create subcategory", self)
        self.act_create_subcategory.triggered.connect(self.create_subcategory)
        self.manage_menu.addAction(self.act_create_subcategory)
        self.act_update_subcategory = QAction("Update subcategory", self)
        self.act_update_subcategory.triggered.connect(self.update_subcategory)
        self.act_update_subcategory.setEnabled(False)
        self.manage_menu.addAction(self.act_update_subcategory)
        self.act_delete_subcategory = QAction("Delete subcategory", self)
        self.act_delete_subcategory.triggered.connect(self.delete_subcategory)
        self.act_delete_subcategory.setEnabled(False)
        self.manage_menu.addAction(self.act_delete_subcategory)
        self.manage_menu.addSeparator()

        if self.frame_type == TYPE_LIBRARY:
            delete_text = "Delete reference"
        elif self.frame_type == TYPE_PROTOCOL:
            delete_text = "Delete protocol"
        self.act_delete = QAction(delete_text, self)
        self.act_delete.triggered.connect(self.delete_entry)
        self.act_delete.setEnabled(False)
        self.manage_menu.addAction(self.act_delete)
        self.btn_manage.setMenu(self.manage_menu)

        # Edit and selections properties
        self.view_tree.header().hide()
        self.view_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view_tree.setDragDropMode(QAbstractItemView.InternalMove)

        # Setup the main layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.frame)
        self.setLayout(self.main_layout)

    def update_category(self):
        """ Show a dialog to update a category """

        # Get the category informations
        index = self.view_tree.selectionModel().currentIndex()

        if self.is_category(index):
            name = index.data(Qt.DisplayRole)
            selected_id = index.data(Qt.UserRole)

            # Show the dialog
            category = Category(name, selected_id)
            category.lbl_title.setText("Update a category")
            category.setWindowModality(Qt.WindowModal)
            category.setParent(self, Qt.Sheet)
            category.show()
            category.accepted.connect(self.show_list)

    def create_category(self):
        """ Show a sheet dialog to create a new category """
        category = Category()
        category.lbl_title.setText("Create a new category")
        category.setWindowModality(Qt.WindowModal)
        category.setParent(self, Qt.Sheet)
        category.show()
        category.accepted.connect(self.show_list)

    def delete_category(self):
        """ Delete an existing category """

        # Get the category informations
        index = self.view_tree.selectionModel().currentIndex()

        if self.is_category(index):
            selected_id = index.data(Qt.UserRole)

            try:
                database.delete_category(selected_id)
            except sqlite3.Error as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.FOREIGN_KEY_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Unable to delete category")
                    message.setInformativeText("Only empty category can be deleted.")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                    return
                else:
                    message = QMessageBox(QMessageBox.Warning, "Error deleting the category",
                                          "An error occurred while deleting the category.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                    return
            self.show_list()

    def create_subcategory(self):
        """ Show a sheet dialog to create a new subcategory """
        category = Subcategory()
        category.lbl_title.setText("Create a new subcategory")
        category.setWindowModality(Qt.WindowModal)
        category.setParent(self, Qt.Sheet)
        category.show()
        category.accepted.connect(self.show_list)

    def update_subcategory(self):
        """ Show a dialog to update a category """

        # Get the subcategory informations
        index = self.view_tree.selectionModel().currentIndex()

        if self.is_subcategory(index):
            name = index.data(Qt.DisplayRole)
            selected_id = index.data(Qt.UserRole)

            # Show the dialog
            subcategory = Subcategory(name, selected_id)
            subcategory.lbl_title.setText("Update a subcategory")
            subcategory.setWindowModality(Qt.WindowModal)
            subcategory.setParent(self, Qt.Sheet)
            subcategory.show()
            subcategory.accepted.connect(self.show_list)

    def delete_subcategory(self):
        """ Delete a subcategory """
        # Get the subcategory informations
        index = self.view_tree.selectionModel().currentIndex()

        if self.is_subcategory(index):
            selected_id = index.data(Qt.UserRole)

            try:
                database.delete_subcategory(selected_id)
            except sqlite3.Error as exception:
                error_code = sqlite_error.sqlite_err_handler(str(exception))

                if error_code == sqlite_error.FOREIGN_KEY_CODE:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Unable to delete subcategory")
                    message.setInformativeText("Only empty subcategory can be deleted.")
                    message.setIcon(QMessageBox.Information)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                    return
                else:
                    message = QMessageBox(QMessageBox.Warning, "Error deleting the subcategory",
                                          "An error occurred while deleting the subcategory.", QMessageBox.Ok)
                    message.setWindowTitle("LabNote")
                    message.setDetailedText(str(exception))
                    message.exec()
                    return
            self.show_list()

    def delete_entry(self):
        """ Delete the current entry """
        index = self.view_tree.selectionModel().currentIndex()

        if self.is_entry(index):
            ref_uuid = index.data(Qt.UserRole)
            self.delete.emit(ref_uuid)

    def show_list(self):
        """ Show the category, subcategory and entry list """

        entry_list = None

        try:
            if self.frame_type == TYPE_LIBRARY:
                entry_list = database.select_reference_category()
            elif self.frame_type == TYPE_PROTOCOL:
                entry_list = database.select_protocol_category()

        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the references data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        model = StandardItemModel()
        root = model.invisibleRootItem()

        if entry_list:
            for category in entry_list:
                category_item = QStandardItem(category.name)
                category_item.setData(category.id, Qt.UserRole)
                category_item.setData(self.prepare_category_data_string(category.id), QT_StateRole)
                category_item.setData(LEVEL_CATEGORY, QT_LevelRole)
                category_item.setFont(QFont(self.font().family(), 12, QFont.Bold))
                category_item.setDragEnabled(False)
                root.appendRow(category_item)

                if category.subcategory:
                    for subcategory in category.subcategory:
                        subcategory_item = QStandardItem(subcategory.name)
                        subcategory_item.setData(subcategory.id, Qt.UserRole)
                        subcategory_item.setData(self.prepare_subcategory_data_string(subcategory.id), QT_StateRole)
                        subcategory_item.setData(LEVEL_SUBCATEGORY, QT_LevelRole)
                        subcategory_item.setDragEnabled(False)
                        category_item.appendRow(subcategory_item)

                        if subcategory.entry:
                            for reference in subcategory.entry:
                                author = reference.author.split()[0]
                                label = "{} ({}), {}".format(author, reference.year, reference.title)
                                reference_item = QStandardItem(label)
                                reference_item.setData(reference.uuid, Qt.UserRole)
                                reference_item.setData(LEVEL_ENTRY, QT_LevelRole)
                                reference_item.setForeground(QColor(96, 96, 96))
                                subcategory_item.appendRow(reference_item)
                if category.entry:
                    for reference in category.entry:
                        author = reference.author.split()[0]
                        label = "{} ({}), {}".format(author, reference.year, reference.title)
                        reference_item = QStandardItem(label)
                        reference_item.setData(reference.uuid, Qt.UserRole)
                        reference_item.setData(LEVEL_ENTRY, QT_LevelRole)
                        reference_item.setForeground(QColor(96, 96, 96))
                        category_item.appendRow(reference_item)

        self.view_tree.setModel(model)
        self.view_tree.selectionModel().currentChanged.connect(self.selection_change)
        self.list_displayed.emit()

    def selection_change(self):
        # Get the category informations
        index = self.view_tree.selectionModel().currentIndex()
        hierarchy_level = self.get_hierarchy_level(index)

        self.selection_changed.emit()

        if hierarchy_level == 1:
            self.act_update_subcategory.setEnabled(False)
            self.act_delete_subcategory.setEnabled(False)
            self.act_update_category.setEnabled(True)
            self.act_delete_category.setEnabled(True)
            self.act_delete.setEnabled(False)
        elif hierarchy_level == 2:
            self.act_update_category.setEnabled(False)
            self.act_delete_category.setEnabled(False)
            self.act_delete.setEnabled(False)
            if index.data(QT_LevelRole) == LEVEL_ENTRY:
                self.entry_selected.emit(index.data(Qt.UserRole))
                self.act_delete.setEnabled(True)
            else:
                self.act_update_subcategory.setEnabled(True)
                self.act_delete_subcategory.setEnabled(True)
        elif hierarchy_level == 3:
            self.act_update_subcategory.setEnabled(False)
            self.act_delete_subcategory.setEnabled(False)
            self.act_update_category.setEnabled(False)
            self.act_delete_category.setEnabled(False)
            self.act_delete.setEnabled(True)
            self.entry_selected.emit(index.data(Qt.UserRole))

    def get_subcategory(self):
        """ Return the current subcategory id

        :return int: Subcategory id
        """

        index = self.view_tree.selectionModel().currentIndex()
        hierarchy_level = self.get_hierarchy_level(index)

        if hierarchy_level == 2:
            return index.data(Qt.UserRole)
        elif hierarchy_level == 3:
            return index.parent().data(Qt.UserRole)
        else:
            return None

    def is_category(self, index):
        """ Return true if the index is a category

        :param index: Item index
        :type index: QModelIndex
        :return bool: True if the index is a category
        """
        if index.data(QT_LevelRole) == LEVEL_CATEGORY:
            return True
        return False

    def is_subcategory(self, index):
        """ Return true if the index is a subcategory

        :param index: Item index
        :type index: QModelIndex
        :return bool: True if the index is a subcategory
        """
        if index.data(QT_LevelRole) == LEVEL_SUBCATEGORY:
            return True
        return False

    def is_entry(self, index):
        """ Return true if the index is a reference

        :param index: Item index
        :type index: QModelIndex
        :return bool: True if the index is a reference
        """
        if index.data(QT_LevelRole) == LEVEL_ENTRY:
            return True
        return False

    def get_hierarchy_level(self, index):
        """ Get the hierarchy level for the index

        :param index: Item index
        :type index: QModelIndex
        :return int: Hierarchy level
        """
        hierarchy_level = 1
        seek_root = index

        while seek_root.parent() != QModelIndex():
            seek_root = seek_root.parent()
            hierarchy_level = hierarchy_level + 1

        return hierarchy_level

    def get_category(self):
        """ Return the current category id

        :return int: Category id
        """

        index = self.view_tree.selectionModel().currentIndex()
        hierarchy_level = self.get_hierarchy_level(index)

        if hierarchy_level == 1:
            return index.data(Qt.UserRole)
        elif hierarchy_level == 2:
            return index.parent().data(Qt.UserRole)
        elif hierarchy_level == 3:
            parent = index.parent()
            return parent.parent().data(Qt.UserRole)
        else:
            return None

    def get_user_data(self):
        """ Return the data in the current item for user role """
        index = self.view_tree.selectionModel().currentIndex()
        return index.data(Qt.UserRole)

    def get_current_level(self):
        """ Return the level of the current item """
        index = self.view_tree.selectionModel().currentIndex()
        return index.data(QT_LevelRole)

    def prepare_category_data_string(self, id):
        """ Add a 'C' before the category data string

        This is required to save the treeview state as the category and subcategory id are identical

        :param id: Category id
        :type id: int
        :return str: C + id
        """
        return "C{}".format(id)

    def prepare_subcategory_data_string(self, id):
        """ Add an 'S' before the subcategory data string

        This is required to save the treeview state as the category and subcategory id are identical

        :param id: Subcategory id
        :type id: int
        :return str: S + id
        """
        return "S{}".format(id)


class TextEditor(QWidget, Ui_TextEditor):
    """ Complex text editor """
    def __init__(self):
        super(TextEditor, self).__init__()
        self.setupUi(self)

