"""
This module contain the classes responsible for launching and managing the library dialog.
"""

# Python import
import sip
import sqlite3
import uuid

# PyQt import
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QMenu, QAction, QMessageBox, QFormLayout,\
    QAbstractItemView, QTreeView
from PyQt5.QtCore import Qt, QRegExp, QModelIndex, QSettings
from PyQt5.QtGui import QFont, QRegExpValidator, QStandardItemModel, QStandardItem, QColor

# Project import
from labnote.ui.ui_library import Ui_Library
from labnote.core import stylesheet, textedit, sqlite_error, data
from labnote.interface.dialog.category import Category, Subcategory
from labnote.utils import database

# Constant definition

# Reference type
TYPE_ARTICLE = 0
TYPE_BOOK = 1
TYPE_CHAPTER = 2

# Data type
QT_LevelRole = Qt.UserRole+1
QT_StateRole = QT_LevelRole+1

# Level type
LEVEL_CATEGORY = 101
LEVEL_SUBCATEGORY = 102
LEVEL_REFERENCE = 103


class Library(QDialog, Ui_Library):
    """
    Class responsible of managing the library window interface.
    """

    # Class variable
    grid_layout = None
    creating_reference = False  # True when a new reference is created

    def __init__(self, parent=None):
        super(Library, self).__init__(parent)
        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Show the dialog
        self.show()

    def init_ui(self):
        self.setWindowTitle("LabNote - Library")
        self.setSizeGripEnabled(True)

        # Create the treeview
        self.treeview = TreeView()
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectRows)
        stylesheet.set_style_sheet(self.treeview, ":/StyleSheet/style-sheet/library/treeview.qss")
        self.frame.layout().insertWidget(1, self.treeview)

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/library.qss")

        # Remove focus rectangle
        self.treeview.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.txt_key.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.txt_search.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Key size
        self.lbl_key.setFixedSize(102, 21)

        # Clear the form
        self.clear_form()

        # Key validator
        validator = QRegExpValidator(QRegExp("^[a-zA-Z0-9_]+$"))
        self.txt_key.setValidator(validator)

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
        self.btn_manage.setMenu(self.manage_menu)

        # Focus policy
        self.treeview.setFocusPolicy(self.treeview.focusPolicy() ^ Qt.TabFocus)
        self.txt_search.setFocusPolicy(self.txt_search.focusPolicy() ^ Qt.TabFocus)

        # Manage list
        self.show_list()
        self.treeview.header().hide()
        self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.treeview.setDragDropMode(QAbstractItemView.InternalMove)

    def init_connection(self):
        self.comboBox.currentTextChanged.connect(self.show_field)
        self.btn_add.clicked.connect(self.start_creating_reference)
        self.btn_save.clicked.connect(self.process_reference)
        self.treeview.collapsed.connect(self.save_treeview_state)
        self.treeview.expanded.connect(self.save_treeview_state)

    def selection_changed(self):
        # Get the category informations
        self.clear_form()

        index = self.treeview.selectionModel().currentIndex()
        hierarchy_level = self.get_hierarchy_level(index)

        if hierarchy_level == 1:
            self.act_update_subcategory.setEnabled(False)
            self.act_delete_subcategory.setEnabled(False)
            self.act_update_category.setEnabled(True)
            self.act_delete_category.setEnabled(True)
        elif hierarchy_level == 2:
            self.act_update_subcategory.setEnabled(True)
            self.act_delete_subcategory.setEnabled(True)
            self.act_update_category.setEnabled(False)
            self.act_delete_category.setEnabled(False)
            if index.data(QT_LevelRole) == LEVEL_REFERENCE:
                self.show_reference_details(index.data(Qt.UserRole))
        elif hierarchy_level == 3:
            self.act_update_subcategory.setEnabled(False)
            self.act_delete_subcategory.setEnabled(False)
            self.act_update_category.setEnabled(False)
            self.act_delete_category.setEnabled(False)
            if index.data(QT_LevelRole) == LEVEL_REFERENCE:
                self.show_reference_details(index.data(Qt.UserRole))

    def show_reference_details(self, uuid):
        """ Show a reference details when it is selected """
        try:
            reference = database.select_reference(uuid)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the reference data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.enable_all(True)

        if reference['type'] == TYPE_ARTICLE:
            self.txt_key.setText(data.receive_string(reference['key']))
            self.txt_author.setText(data.receive_string(reference['author']))
            self.txt_title.setText(data.receive_string(reference['title']))
            self.txt_journal.setText(data.receive_string(reference['journal']))
            self.txt_year.setText(data.receive_string(reference['year']))
            self.txt_volume.setText(data.receive_string(reference['volume']))
            self.txt_issue.setText(data.receive_string(reference['issue']))
            self.txt_pages.setText(data.receive_string(reference['pages']))
            self.txt_description.setHtml(data.receive_string(reference['description']))
            self.txt_abstract.setHtml(data.receive_string(reference['abstract']))
        elif reference['type'] == TYPE_BOOK:
            self.txt_key.setText(data.receive_string(reference['key']))
            self.txt_author.setText(data.receive_string(reference['author']))
            self.txt_title.setText(data.receive_string(reference['title']))
            self.txt_year.setText(data.receive_string(reference['year']))
            self.txt_publisher.setText(data.receive_string(reference['publisher']))
            self.txt_place_published.settext(data.receive_string(reference['place']))
            self.txt_volume.setText(data.receive_string(reference['volume']))
            self.txt_pages.setText(data.receive_string(reference['pages']))
            self.txt_edition.settext(data.receive_string(reference['edition']))
            self.txt_description.setHtml(data.receive_string(reference['description']))
            self.txt_abstract.setHtml(data.receive_string(reference['abstract']))
        elif reference['type'] == TYPE_CHAPTER:
            self.txt_key.setText(data.receive_string(reference['key']))
            self.txt_chapter.setText(data.receive_string(reference['chapter']))
            self.txt_author.setText(data.receive_string(reference['author']))
            self.txt_title.setText(data.receive_string(reference['title']))
            self.txt_year.setText(data.receive_string(reference['year']))
            self.txt_editor.setText(data.receive_string(reference['editor']))
            self.txt_publisher.setText(data.receive_string(reference['publisher']))
            self.txt_place_published.settext(data.receive_string(reference['place']))
            self.txt_volume.setText(data.receive_string(reference['volume']))
            self.txt_pages.setText(data.receive_string(reference['pages']))
            self.txt_edition.settext(data.receive_string(reference['edition']))
            self.txt_description.setHtml(data.receive_string(reference['description']))
            self.txt_abstract.setHtml(data.receive_string(reference['abstract']))

    def show_list(self):
        """ Show the category, subcategory and references list """

        reference_list = None

        try:
            reference_list = database.select_reference_category()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the references data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        model = StandardItemModel()
        root = model.invisibleRootItem()

        if reference_list:
            for category in reference_list:
                category_item = QStandardItem(category.name)
                category_item.setData(category.id, Qt.UserRole)
                category_item.setData(self.prepare_category_data_string(category.id), QT_StateRole)
                category_item.setData(LEVEL_CATEGORY, QT_LevelRole)
                category_item.setFont(QFont(self.font().family(), 12, QFont.Bold))
                root.appendRow(category_item)

                if category.subcategory:
                    for subcategory in category.subcategory:
                        subcategory_item = QStandardItem(subcategory.name)
                        subcategory_item.setData(subcategory.id, Qt.UserRole)
                        subcategory_item.setData(self.prepare_subcategory_data_string(subcategory.id), QT_StateRole)
                        subcategory_item.setData(LEVEL_SUBCATEGORY, QT_LevelRole)
                        category_item.appendRow(subcategory_item)

                        if subcategory.reference:
                            for reference in subcategory.reference:
                                author = reference.author.split()[0]
                                label = "{} ({}), {}".format(author, reference.year, reference.title)
                                reference_item = QStandardItem(label)
                                reference_item.setData(reference.uuid, Qt.UserRole)
                                reference_item.setData(LEVEL_REFERENCE, QT_LevelRole)
                                reference_item.setForeground(QColor(96, 96, 96))
                                subcategory_item.appendRow(reference_item)
                if category.reference:
                    for reference in category.reference:
                        author = reference.author.split()[0]
                        label = "{} ({}), {}".format(author, reference.year, reference.title)
                        reference_item = QStandardItem(label)
                        reference_item.setData(reference.uuid, Qt.UserRole)
                        reference_item.setData(LEVEL_REFERENCE, QT_LevelRole)
                        reference_item.setForeground(QColor(96, 96, 96))
                        category_item.appendRow(reference_item)

        self.treeview.setModel(model)
        self.treeview.selectionModel().currentChanged.connect(self.selection_changed)
        self.restore_treeview_state()

    def start_creating_reference(self):
        """ Enable new reference creation """
        index = self.treeview.selectionModel().currentIndex()
        if index.data(QT_LevelRole) == LEVEL_CATEGORY or \
                index.data(QT_LevelRole) == LEVEL_SUBCATEGORY or \
                index.data(QT_LevelRole) == LEVEL_REFERENCE:
            self.article_field()
            self.txt_key.clear()
            self.creating_reference = True
            self.enable_all(True)

    def clear_form(self):
        """ Clear all data in the form """
        self.creating_reference = False
        self.txt_key.clear()
        self.article_field()
        self.enable_all(False)

    def get_category(self, index):
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
        elif hierarchy_level == 3:
            parent = index.parent()
            return parent.parent().data(Qt.UserRole)
        else:
            return None

    def get_subcategory(self, index):
        """ Return a subcategory id

        :param index: Item index
        :type index: QModelIndex
        :return int: Subcategory id
        """
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
        if self.get_hierarchy_level(index) == 1:
            return True
        return False

    def is_subcategory(self, index):
        """ Return true if the index is a subcategory

        :param index: Item index
        :type index: QModelIndex
        :return bool: True if the index is a subcategory
        """
        if self.get_hierarchy_level(index) == 2:
            return True
        return False

    def is_reference(self, index):
        """ Return true if the index is a reference

        :param index: Item index
        :type index: QModelIndex
        :return bool: True if the index is a reference
        """
        if self.get_hierarchy_level(index) == 3:
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

    def update_category(self):
        """ Show a dialog to update a category """

        # Get the category informations
        index = self.treeview.selectionModel().currentIndex()

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
        index = self.treeview.selectionModel().currentIndex()

        if self.is_category(index):
            selected_id = index.data(Qt.UserRole)

            try:
                database.delete_ref_category(selected_id)
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
        index = self.treeview.selectionModel().currentIndex()

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
        # Get the subcategory informations
        index = self.treeview.selectionModel().currentIndex()

        if self.is_subcategory(index):
            selected_id = index.data(Qt.UserRole)

            try:
                database.delete_ref_subcategory(selected_id)
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

    def delete_layout(self, layout):
        """ Delete any layout """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.delete_layout(item.layout())
            sip.delete(layout)

    def enable_all(self, enable):
        """ Disable all items in the layout

        :param enable: Enable state
        :type enable: bool
        """
        self.lbl_key.setEnabled(enable)
        self.txt_key.setEnabled(enable)
        self.comboBox.setEnabled(enable)
        self.btn_save.setEnabled(enable)

        if self.grid_layout is not None:
            for position in range(0, self.grid_layout.count()):
                item = self.grid_layout.itemAt(position)
                widget = item.widget()
                if widget is not None:
                    widget.setEnabled(enable)

    def process_reference(self):
        """ Create the reference in the database """

        key = self.txt_key.text()

        if key:
            # Get the current index
            index = self.treeview.selectionModel().currentIndex()

            category_id = self.get_category(index)
            subcategory_id = self.get_subcategory(index)

            if category_id:
                ref_type = self.comboBox.currentText()

                if ref_type == "Article":
                    author = data.prepare_string(self.txt_author.text())
                    title = data.prepare_string(self.txt_title.text())
                    journal = data.prepare_string(self.txt_journal.text())
                    year = data.prepare_string_number(self.txt_year.text())
                    volume = data.prepare_string_number(self.txt_volume.text())
                    issue = data.prepare_string_number(self.txt_issue.text())
                    pages = data.prepare_string(self.txt_pages.text())
                    description = data.prepare_textedit(self.txt_description)
                    abstract = data.prepare_textedit(self.txt_abstract)
                elif ref_type == "Book":
                    author = data.prepare_string(self.txt_author.text())
                    title = data.prepare_string(self.txt_title.text())
                    year = data.prepare_string_number(self.txt_year.text())
                    publisher = data.prepare_string(self.txt_publisher.text())
                    place = data.prepare_string(self.txt_place_published.text())
                    volume = data.prepare_string_number(self.txt_volume.text())
                    pages = data.prepare_string(self.txt_pages.text())
                    edition = data.prepare_string_number(self.txt_edition.text())
                    description = data.prepare_textedit(self.txt_description)
                    abstract = data.prepare_textedit(self.txt_abstract)
                elif ref_type == "Chapter":
                    author = data.prepare_string(self.txt_author.text())
                    chapter = data.prepare_string(self.txt_chapter.text())
                    title = data.prepare_string(self.txt_title.text())
                    year = data.prepare_string_number(self.txt_year.text())
                    editor = data.prepare_string(self.txt_editor.text())
                    publisher = data.prepare_string(self.txt_publisher.text())
                    place = data.prepare_string(self.txt_place_published.text())
                    volume = data.prepare_string_number(self.txt_volume.text())
                    pages = data.prepare_string(self.txt_pages.text())
                    edition = data.prepare_string_number(self.txt_edition.text())
                    description = data.prepare_textedit(self.txt_description)
                    abstract = data.prepare_textedit(self.txt_abstract)

                if self.creating_reference:
                    ref_uuid = data.uuid_bytes(uuid.uuid4())
                    try:
                        if ref_type == "Article":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, ref_type=TYPE_ARTICLE,
                                                category_id=category_id, subcategory_id=subcategory_id, author=author,
                                                title=title, journal=journal, year=year, volume=volume, issue=issue,
                                                pages=pages, description=description, abstract=abstract)
                        elif ref_type == "Book":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=category_id,
                                                subcategory_id=subcategory_id, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                ref_type=TYPE_BOOK)
                        elif ref_type == "Chapter":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=category_id,
                                                subcategory_id=subcategory_id, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                chapter=chapter, editor=editor, ref_type=TYPE_CHAPTER)
                    except sqlite3.Error as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create reference")
                            message.setInformativeText("The reference key must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create reference")
                            message.setInformativeText("The reference key must be unique.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to create reference",
                                                  "An error occurred while creating the reference.", QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return
                else:
                    ref_uuid = index.data(Qt.UserRole)
                    try:
                        if ref_type == "Article":
                            database.update_ref(ref_uuid=ref_uuid, ref_key=key, ref_type=TYPE_ARTICLE, author=author,
                                                title=title, journal=journal, year=year, volume=volume, issue=issue,
                                                pages=pages, description=description, abstract=abstract)
                        elif ref_type == "Book":
                            database.update_ref(ref_uuid=ref_uuid, ref_key=key, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                ref_type=TYPE_BOOK)
                        elif ref_type == "Chapter":
                            database.update_ref(ref_uuid=ref_uuid, ref_key=key, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                chapter=chapter, editor=editor, ref_type=TYPE_CHAPTER)
                    except sqlite3.Error as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create reference")
                            message.setInformativeText("The reference key must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create reference")
                            message.setInformativeText("The reference key must be unique.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to create reference",
                                                  "An error occurred while creating the reference.", QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return
                self.show_list()

    def reset_fields(self):
        self.txt_key.clear()
        self.article_field()
        self.enable_all(False)

    def show_field(self, text):
        """ Show the field related to a specific type of literature """

        fields = self.save_fields()

        # Show appropriate fields
        if text == "Article":
            self.article_field(fields=fields)
        elif text == "Book":
            self.book_field(fields=fields)
        else:
            self.chapter_field(fields=fields)

    def create_grid(self):
        """ Create the grid layout

        :return QGridLayout: Grid Layout
        """
        self.grid_layout = QGridLayout()
        self.grid_layout.setColumnMinimumWidth(0, 110)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 12, 0)

    def prepare_grid(self):
        """ Delete the grid layout """
        self.delete_layout(self.grid_layout)
        self.create_grid()

    def article_field(self, fields=None):
        """ Show all the article related fields in the layout """
        self.prepare_grid()

        self.lbl_author = QLabel("Author")
        self.lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_author, 0, 0)
        self.txt_author = LineEdit()
        self.grid_layout.addWidget(self.txt_author, 0, 1)

        self.lbl_title = QLabel("Title")
        self.lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_title, 1, 0)
        self.txt_title = LineEdit()
        self.grid_layout.addWidget(self.txt_title, 1, 1)

        self.lbl_journal = QLabel("Journal")
        self.lbl_journal.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_journal, 2, 0)
        self.txt_journal = LineEdit()
        self.grid_layout.addWidget(self.txt_journal, 2, 1)

        self.lbl_year = QLabel("Year")
        self.lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_year, 3, 0)
        self.txt_year = YearLineEdit()
        self.grid_layout.addWidget(self.txt_year, 3, 1)

        self.lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(self.lbl_volume, 4, 0)
        self.txt_volume = NumberLineEdit()
        self.grid_layout.addWidget(self.txt_volume, 4, 1)

        self.lbl_issue = QLabel("Issue")
        self.grid_layout.addWidget(self.lbl_issue, 5, 0)
        self.txt_issue = NumberLineEdit()
        self.grid_layout.addWidget(self.txt_issue, 5, 1)

        self.lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(self.lbl_pages, 6, 0)
        self.txt_pages = PagesLineEdit()
        self.grid_layout.addWidget(self.txt_pages, 6, 1)

        self.lbl_description = QLabel("Description")
        self.lbl_description.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.addWidget(self.lbl_description, 7, 0)
        self.txt_description = textedit.TextEdit()
        self.grid_layout.addWidget(self.txt_description, 7, 1)

        self.lbl_abstract = QLabel("Abstract")
        self.lbl_abstract.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.addWidget(self.lbl_abstract, 8, 0)
        self.txt_abstract = textedit.TextEdit()
        self.grid_layout.addWidget(self.txt_abstract, 8, 1)

        if fields:
            self.txt_author.setText(fields['author'])
            self.txt_title.setText(fields['title'])
            self.txt_journal.setText(fields['journal'])
            self.txt_year.setText(fields['year'])
            self.txt_volume.setText(fields['volume'])
            self.txt_issue.setText(fields['issue'])
            self.txt_pages.setText(fields['pages'])

            if fields['description']:
                self.txt_description.setHtml(fields['description'])

            if fields['abstract']:
                self.txt_abstract.setHtml(fields['abstract'])

        self.detail_layout.insertLayout(1, self.grid_layout)

    def save_fields(self):
        """ Save all the article fields

        :return dict: Dictionary with the article fields
        """
        try:
            title = self.txt_title.text()
        except (AttributeError, RuntimeError):
            title = ""

        try:
            publisher = self.txt_publisher.text()
        except (AttributeError, RuntimeError):
            publisher = ""

        try:
            author = self.txt_author.text()
        except (AttributeError, RuntimeError):
            author = ""

        try:
            year = self.txt_year.text()
        except (AttributeError, RuntimeError):
            year = ""

        try:
            editor = self.txt_editor.text()
        except (AttributeError, RuntimeError):
            editor = ""

        try:
            volume = self.txt_volume.text()
        except (AttributeError, RuntimeError):
            volume = ""

        try:
            place = self.txt_place_published.text()
        except (AttributeError, RuntimeError):
            place = ""

        try:
            edition = self.txt_edition.text()
        except (AttributeError, RuntimeError):
            edition = ""

        try:
            if self.txt_journal:
                journal = self.txt_journal.text()
        except (AttributeError, RuntimeError):
            journal = ""

        try:
            chapter = self.txt_chapter.text()
        except (AttributeError, RuntimeError):
            chapter = ""

        try:
            pages = self.txt_pages.text()
        except (AttributeError, RuntimeError):
            pages = ""

        try:
            issue = self.txt_issue.text()
        except (AttributeError, RuntimeError):
            issue = ""

        try:
            if self.txt_description.toPlainText() != "":
                description = self.txt_description.toHtml()
            else:
                description = None
        except (AttributeError, RuntimeError):
            description = None

        try:
            if self.txt_abstract.toPlainText() != "":
                abstract = self.txt_abstract.toHtml()
            else:
                abstract = None
        except (AttributeError, RuntimeError):
            abstract = None

        return {'title': title,
                'publisher': publisher,
                'year': year,
                'author': author,
                'editor': editor,
                'volume': volume,
                'place': place,
                'edition': edition,
                'journal': journal,
                'chapter': chapter,
                'pages': pages,
                'issue': issue,
                'description': description,
                'abstract': abstract}

    def book_field(self, fields=None):
        """ Show all the book related fields in the layout """
        self.prepare_grid()

        self.lbl_author = QLabel("Author")
        self.lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_author, 0, 0)
        self.txt_author = LineEdit()
        self.grid_layout.addWidget(self.txt_author, 0, 1)

        self.lbl_title = QLabel("Title")
        self.lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_title, 1, 0)
        self.txt_title = LineEdit()
        self.grid_layout.addWidget(self.txt_title, 1, 1)

        self.lbl_year = QLabel("Year")
        self.lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_year, 2, 0)
        self.txt_year = YearLineEdit()
        self.grid_layout.addWidget(self.txt_year, 2, 1)

        self.lbl_publisher = QLabel("Publisher")
        self.lbl_publisher.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_publisher, 3, 0)
        self.txt_publisher = LineEdit()
        self.grid_layout.addWidget(self.txt_publisher, 3, 1)

        self.lbl_place_published = QLabel("Place published")
        self.grid_layout.addWidget(self.lbl_place_published, 4, 0)
        self.txt_place_published = LineEdit()
        self.grid_layout.addWidget(self.txt_place_published, 4, 1)

        self.lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(self.lbl_volume, 5, 0)
        self.txt_volume = NumberLineEdit()
        self.grid_layout.addWidget(self.txt_volume, 5, 1)

        self.lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(self.lbl_pages, 6, 0)
        self.txt_pages = PagesLineEdit()
        self.grid_layout.addWidget(self.txt_pages, 6, 1)

        self.lbl_edition = QLabel("Edition")
        self.grid_layout.addWidget(self.lbl_edition, 7, 0)
        self.txt_edition = LineEdit()
        self.grid_layout.addWidget(self.txt_edition, 7, 1)

        self.lbl_description = QLabel("Description")
        self.grid_layout.addWidget(self.lbl_description, 8, 0)
        self.txt_description = textedit.TextEdit()
        self.grid_layout.addWidget(self.txt_description, 8, 1)

        self.lbl_abstract = QLabel("Abstract")
        self.grid_layout.addWidget(self.lbl_abstract, 9, 0)
        self.txt_abstract = textedit.TextEdit()
        self.grid_layout.addWidget(self.txt_abstract, 9, 1)

        if fields:
            self.txt_author.setText(fields['author'])
            self.txt_title.setText(fields['title'])
            self.txt_year.setText(fields['year'])
            self.txt_publisher.setText(fields['publisher'])
            self.txt_place_published.setText(fields['place'])
            self.txt_volume.setText(fields['volume'])
            self.txt_pages.setText(fields['pages'])
            self.txt_edition.setText(fields['edition'])

            if fields['description']:
                self.txt_description.setHtml(fields['description'])

            if fields['abstract']:
                self.txt_abstract.setHtml(fields['abstract'])


        self.detail_layout.insertLayout(1, self.grid_layout)

    def chapter_field(self, fields=None):
        """ Show all the chapter related fields in the layout """
        self.prepare_grid()

        self.lbl_author = QLabel("Author")
        self.lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_author, 0, 0)
        self.txt_author = LineEdit()
        self.grid_layout.addWidget(self.txt_author, 0, 1)

        self.lbl_chapter = QLabel("Chapter")
        self.lbl_chapter.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_chapter, 1, 0)
        self.txt_chapter = LineEdit()
        self.grid_layout.addWidget(self.txt_chapter, 1, 1)

        self.lbl_title = QLabel("Book title")
        self.lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_title, 2, 0)
        self.txt_title = LineEdit()
        self.grid_layout.addWidget(self.txt_title, 2, 1)

        self.lbl_year = QLabel("Year")
        self.lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_year, 3, 0)
        self.txt_year = YearLineEdit()
        self.grid_layout.addWidget(self.txt_year, 3, 1)

        self.lbl_editor = QLabel("Editor")
        self.grid_layout.addWidget(self.lbl_editor, 4, 0)
        self.txt_editor = LineEdit()
        self.grid_layout.addWidget(self.txt_editor, 4, 1)

        self.lbl_publisher = QLabel("Publisher")
        self.grid_layout.addWidget(self.lbl_publisher, 5, 0)
        self.txt_publisher = LineEdit()
        self.grid_layout.addWidget(self.txt_publisher, 5, 1)

        self.lbl_place_published = QLabel("Place published")
        self.grid_layout.addWidget(self.lbl_place_published, 6, 0)
        self.txt_place_published = LineEdit()
        self.grid_layout.addWidget(self.txt_place_published, 6, 1)

        self.lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(self.lbl_volume, 7, 0)
        self.txt_volume = NumberLineEdit()
        self.grid_layout.addWidget(self.txt_volume, 7, 1)

        self.lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(self.lbl_pages, 8, 0)
        self.txt_pages = PagesLineEdit()
        self.grid_layout.addWidget(self.txt_pages, 8, 1)

        self.lbl_edition = QLabel("Edition")
        self.grid_layout.addWidget(self.lbl_edition, 9, 0)
        self.txt_edition = NumberLineEdit()
        self.grid_layout.addWidget(self.txt_edition, 9, 1)

        self.lbl_description = QLabel("Description")
        self.grid_layout.addWidget(self.lbl_description, 10, 0)
        self.txt_description = textedit.TextEdit()
        self.grid_layout.addWidget(self.txt_description, 10, 1)

        self.lbl_abstract = QLabel("Abstract")
        self.grid_layout.addWidget(self.lbl_abstract, 11, 0)
        self.txt_abstract = textedit.TextEdit()
        self.grid_layout.addWidget(self.txt_abstract, 11, 1)

        if fields:
            self.txt_author.setText(fields['author'])
            self.txt_chapter.setText(fields['chapter'])
            self.txt_title.setText(fields['title'])
            self.txt_year.setText(fields['year'])
            self.txt_editor.setText(fields['editor'])
            self.txt_publisher.setText(fields['publisher'])
            self.txt_place_published.setText(fields['place'])
            self.txt_volume.setText(fields['volume'])
            self.txt_pages.setText(fields['pages'])
            self.txt_edition.setText(fields['edition'])

            if fields['description']:
                self.txt_description.setHtml(fields['description'])

            if fields['abstract']:
                self.txt_abstract.setHtml(fields['abstract'])

        self.detail_layout.insertLayout(1, self.grid_layout)

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

    def closeEvent(self, event):
        self.save_treeview_state()
        event.accept()

    def save_treeview_state(self):
        """ Save the treeview expanded state """

        # Generate list
        expanded_item = []
        for index in self.treeview.model().get_persistant_index_list():
            if self.treeview.isExpanded(index) and index.data(QT_StateRole):
                expanded_item.append(index.data(QT_StateRole))

        # Save list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Library")
        settings.setValue("ExpandedItem", expanded_item)
        settings.endGroup()

    def restore_treeview_state(self):
        """ Restore the treeview expended state """

        # Get list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Library")
        expanded_item = settings.value("ExpandedItem")
        selected_item = settings.value("SelectedItem")
        settings.endGroup()

        model = self.treeview.model()

        if expanded_item:
            for item in expanded_item:
                match = model.match(model.index(0, 0), QT_StateRole, item, 1, Qt.MatchRecursive)

                if match:
                    self.treeview.setExpanded(match[0], True)


class TreeView(QTreeView):
    """ Custom tree view class """


class StandardItemModel(QStandardItemModel):
    """ Custom standard item model class """
    def get_persistant_index_list(self):
        return self.persistentIndexList()


class LineEdit(QLineEdit):
    """ Lineedit used in the form """
    def __init__(self):
        super(LineEdit, self).__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


class YearLineEdit(LineEdit):
    """ Lineedit used for the year """
    def __init__(self):
        super(YearLineEdit, self).__init__()

        validator = QRegExpValidator(QRegExp("^[0-9]{4}$"))
        self.setValidator(validator)


class NumberLineEdit(LineEdit):
    """ Lineedit used in the number only fields """
    def __init__(self):
        super(NumberLineEdit, self).__init__()

        validator = QRegExpValidator(QRegExp("^[0-9]{5}$"))
        self.setValidator(validator)


class PagesLineEdit(LineEdit):
    """ Lineedit used for the pages """
    def __init__(self):
        super(PagesLineEdit, self).__init__()

        validator = QRegExpValidator(QRegExp("^[0-9]{0,5}( - |-)[0-9]{0,5}"))
        self.setValidator(validator)
