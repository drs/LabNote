""" This module contains the custom widget used in labnote """

# Python import
import sqlite3
import sip

# PyQt import
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QAction, QMenu, \
    QMessageBox, QAbstractItemView, QPlainTextEdit, QCompleter
from PyQt5.QtGui import QPixmap, QFont, QStandardItem, QColor, QTextCharFormat, QBrush, QPainter, QPen, QIcon, \
    QTextListFormat, QPainterPath, QTextDocument, QRegExpValidator, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, QRectF, QEvent, QRegExp, QItemSelectionModel

# Project import
from labnote.core import stylesheet
from labnote.interface.widget.view import DragDropTreeView
from labnote.interface.widget.model import StandardItemModel
from labnote.interface.dialog.category import Category, Subcategory
from labnote.interface.widget.textedit import CompleterTextEdit, ImageTextEdit
from labnote.interface.widget.lineedit import LineEdit
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
        self.setFixedWidth(240)
        self.frame = QFrame()

        # Set style sheet
        self.frame.setStyleSheet("""
        .QFrame {
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
        QTreeView {
            border: none;
            background-color: rgb(246, 246, 246);
        }
        
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
        self.btn_add.setEnabled(False)
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
        self.view_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
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
                            for entry in subcategory.entry:
                                author = None
                                label = ""
                                if entry.author:
                                    author = entry.author.split()[0]
                                    label = "{}".format(author)
                                if entry.year:
                                    if label != "":
                                        label = "{} ({})".format(label, entry.year)
                                    else:
                                        label = "({})".format(entry.year)
                                if entry.title:
                                    if label != "":
                                        label = "{}, {}".format(label, entry.title)
                                    else:
                                        label = "{}".format(entry.title)
                                reference_item = QStandardItem(label)
                                reference_item.setData(entry.uuid, Qt.UserRole)
                                reference_item.setData(LEVEL_ENTRY, QT_LevelRole)
                                reference_item.setForeground(QColor(96, 96, 96))
                                subcategory_item.appendRow(reference_item)
                if category.entry:
                    for reference in category.entry:
                        author = None
                        label = ""
                        if reference.author:
                            author = reference.author.split()[0]
                            label = "{}".format(author)
                        if reference.year:
                            if label != "":
                                label = "{} ({})".format(label, reference.year)
                            else:
                                label = "({})".format(reference.year)
                        if reference.title:
                            if label != "":
                                label = "{}, {}".format(label, reference.title)
                            else:
                                label = "{}".format(reference.title)
                        reference_item = QStandardItem(label)
                        reference_item.setData(reference.uuid, Qt.UserRole)
                        reference_item.setData(LEVEL_ENTRY, QT_LevelRole)
                        reference_item.setForeground(QColor(96, 96, 96))
                        category_item.appendRow(reference_item)

        self.view_tree.setModel(model)
        self.view_tree.selectionModel().setCurrentIndex(self.view_tree.model().index(0, 0),
                                                        QItemSelectionModel.ClearAndSelect)
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
            self.btn_add.setEnabled(True)
        elif hierarchy_level == 2:
            self.act_update_category.setEnabled(False)
            self.act_delete_category.setEnabled(False)
            self.act_delete.setEnabled(False)
            self.btn_add.setEnabled(True)
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
            self.btn_add.setEnabled(True)
            self.entry_selected.emit(index.data(Qt.UserRole))

    def get_subcategory(self, index):
        """ Return the current subcategory id

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

    def get_category(self, index):
        """ Return the current category id

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

    # Class variable definition
    width_height_ratio = 1

    def __init__(self, editor_type, tag_list=None, reference_list=None, dataset_list=None, protocol_list=None):
        super(TextEditor, self).__init__()
        # Set class variable
        self.tag_list = tag_list
        self.reference_list = reference_list
        self.dataset_list = dataset_list
        self.protocol_list = protocol_list
        self.editor_type = editor_type

        self.setupUi(self)
        self.init_ui()
        self.init_connection()

    def init_ui(self):
        # Insert title text edit
        self.txt_title = QPlainTextEdit()
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        self.txt_title.setFont(font)
        self.txt_title.setPlaceholderText("Untitled experiment")
        self.txt_title.setFixedHeight(48)
        self.title_layout.insertWidget(0, self.txt_title)
        self.title_layout.setStretch(0, 10)

        # Insert key text edit
        self.txt_key = LineEdit()
        self.txt_key.setPlaceholderText("Experiment key")
        self.txt_key.setStyleSheet(" QLineEdit { border: none; padding-left: 2px; } ")
        self.txt_key.setVisible(False)
        self.layout().insertWidget(2, self.txt_key)

        # Insert descrition text edit
        self.txt_description = CompleterTextEdit(tag_list=self.tag_list)
        self.txt_description.setPlaceholderText("Objectives of the experiment")
        self.txt_description.setFixedHeight(74)
        self.layout().insertWidget(3, self.txt_description)

        # Insert textedit in layout
        self.txt_body = ImageTextEdit(editor_type=self.editor_type, reference_list=self.reference_list,
                                      dataset_list=self.dataset_list, protocol_list=self.protocol_list)
        self.txt_body.setStyleSheet("border-top: 0.5px solid rgb(212, 212, 212)")
        self.layout().insertWidget(4, self.txt_body, 10)

        # Set button groups
        self.btn_bold.setProperty("Menu", False)
        self.btn_italic.setProperty("Menu", False)
        self.btn_underline.setProperty("Menu", False)
        self.btn_strikethrough.setProperty("Menu", False)
        self.btn_superscript.setProperty("Menu", False)
        self.btn_subscript.setProperty("Menu", False)
        self.btn_style.setProperty("Menu", True)
        self.btn_color.setProperty("Menu", True)
        self.btn_highlight.setProperty("Menu", True)
        self.btn_list.setProperty("Menu", True)
        self.btn_color.setProperty("IconOnly", True)
        self.btn_highlight.setProperty("IconOnly", True)

        # Image size line edit
        validator = QRegExpValidator(QRegExp("^[0-9]{0,4}$"))
        self.txt_width.setValidator(validator)
        self.txt_height.setValidator(validator)

        # Style menu
        self.act_part = QAction("Part", self)
        self.act_part.setFont(QFont(self.font().family(), 20, 75))
        self.act_section = QAction("Section", self)
        self.act_section.setFont(QFont(self.font().family(), 16, 75))
        self.act_subsection = QAction("Subsection", self)
        self.act_subsection.setFont(QFont(self.font().family(), 14, 75))
        self.act_subsubsection = QAction("Subsubsection", self)
        self.act_subsubsection.setFont(QFont(self.font().family(), 12, 75))
        self.act_body = QAction("Body", self)
        self.act_body.setFont(QFont(self.font().family(), 12, 50))
        self.act_note = QAction("Note", self)
        self.act_note.setFont(QFont(self.font().family(), 10, 50))

        self.style_menu = QMenu(self)
        self.style_menu.addAction(self.act_part)
        self.style_menu.addAction(self.act_section)
        self.style_menu.addAction(self.act_subsection)
        self.style_menu.addAction(self.act_subsubsection)
        self.style_menu.addAction(self.act_body)
        self.style_menu.addAction(self.act_note)
        self.btn_style.setMenu(self.style_menu)

        # Highlight color menu
        self.act_clear_highlight = QAction("Clear", self)
        clear_highlight_icon = self.draw_color(Qt.white, Qt.lightGray)
        self.act_clear_highlight.setIcon(clear_highlight_icon)

        self.act_red_highlight = QAction("Red", self)
        red_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['red'].color, common.HIGHLIGHT_COLOR['red'].dark_shade)
        self.act_red_highlight.setIcon(red_highlight_icon)

        self.act_orange_highlight = QAction("Orange", self)
        orange_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['orange'].color, common.HIGHLIGHT_COLOR['orange'].dark_shade)
        self.act_orange_highlight.setIcon(orange_highlight_icon)

        self.act_yellow_highlight = QAction("Yellow", self)
        yellow_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['yellow'].color, common.HIGHLIGHT_COLOR['yellow'].dark_shade)
        self.act_yellow_highlight.setIcon(yellow_highlight_icon)

        self.act_green_highlight = QAction("Green", self)
        green_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['green'].color, common.HIGHLIGHT_COLOR['green'].dark_shade)
        self.act_green_highlight.setIcon(green_highlight_icon)

        self.act_blue_highlight = QAction("Blue", self)
        blue_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['blue'].color, common.HIGHLIGHT_COLOR['blue'].dark_shade)
        self.act_blue_highlight.setIcon(blue_highlight_icon)

        self.act_purple_highlight = QAction("Purple", self)
        purple_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['purple'].color, common.HIGHLIGHT_COLOR['purple'].dark_shade)
        self.act_purple_highlight.setIcon(purple_highlight_icon)

        self.act_gray_highlight = QAction("Gray", self)
        gray_highlight_icon = self.draw_color(
            common.HIGHLIGHT_COLOR['gray'].color, common.HIGHLIGHT_COLOR['gray'].dark_shade)
        self.act_gray_highlight.setIcon(gray_highlight_icon)

        self.highlight_menu = QMenu(self)
        self.highlight_menu.addAction(self.act_clear_highlight)
        self.highlight_menu.addAction(self.act_red_highlight)
        self.highlight_menu.addAction(self.act_orange_highlight)
        self.highlight_menu.addAction(self.act_yellow_highlight)
        self.highlight_menu.addAction(self.act_green_highlight)
        self.highlight_menu.addAction(self.act_blue_highlight)
        self.highlight_menu.addAction(self.act_purple_highlight)
        self.highlight_menu.addAction(self.act_gray_highlight)
        self.btn_highlight.setMenu(self.highlight_menu)

        # Text color menu
        self.act_black_text = QAction("Black", self)
        black_text_icon = self.draw_color(common.TEXT_COLOR['black'].color, common.TEXT_COLOR['black'].dark_shade)
        self.act_black_text.setIcon(black_text_icon)

        self.act_gray_text = QAction("Gray", self)
        gray_text_icon = self.draw_color(common.TEXT_COLOR['gray'].color, common.TEXT_COLOR['gray'].dark_shade)
        self.act_gray_text.setIcon(gray_text_icon)

        self.act_red_text = QAction("Red", self)
        red_text_icon = self.draw_color(common.TEXT_COLOR['red'].color, common.TEXT_COLOR['red'].dark_shade)
        self.act_red_text.setIcon(red_text_icon)

        self.act_orange_text = QAction("Orange", self)
        orange_text_icon = self.draw_color(common.TEXT_COLOR['orange'].color, common.TEXT_COLOR['orange'].dark_shade)
        self.act_orange_text.setIcon(orange_text_icon)

        self.act_yellow_text = QAction("Yellow", self)
        yellow_text_icon = self.draw_color(common.TEXT_COLOR['yellow'].color, common.TEXT_COLOR['yellow'].dark_shade)
        self.act_yellow_text.setIcon(yellow_text_icon)

        self.act_green_text = QAction("Green", self)
        green_text_icon = self.draw_color(common.TEXT_COLOR['green'].color, common.TEXT_COLOR['green'].dark_shade)
        self.act_green_text.setIcon(green_text_icon)

        self.act_blue_text = QAction("Blue", self)
        blue_text_icon = self.draw_color(common.TEXT_COLOR['blue'].color, common.TEXT_COLOR['blue'].dark_shade)
        self.act_blue_text.setIcon(blue_text_icon)

        self.act_purple_text = QAction("Purple", self)
        purple_text_icon = self.draw_color(common.TEXT_COLOR['purple'].color, common.TEXT_COLOR['purple'].dark_shade)
        self.act_purple_text.setIcon(purple_text_icon)

        self.color_menu = QMenu(self)
        self.color_menu.addAction(self.act_black_text)
        self.color_menu.addAction(self.act_gray_text)
        self.color_menu.addAction(self.act_red_text)
        self.color_menu.addAction(self.act_orange_text)
        self.color_menu.addAction(self.act_yellow_text)
        self.color_menu.addAction(self.act_green_text)
        self.color_menu.addAction(self.act_blue_text)
        self.color_menu.addAction(self.act_purple_text)
        self.btn_color.setMenu(self.color_menu)

        # List menu
        self.act_no_list = QAction("No list", self)
        self.act_bullet_list = QAction("•  Bullet", self)
        self.act_numbered_list = QAction("1. Numbered", self)
        self.act_roman_list = QAction("I.  Roman numbered", self)
        self.act_uppercase_list = QAction("A. Uppercase letters", self)
        self.act_lowercase_list = QAction("a. Lowercase letters", self)
        self.act_increase_indent = QAction("Increase indentation")
        self.act_decrease_indent = QAction("Decrease indentation")

        self.list_menu = QMenu(self)
        self.list_menu.addAction(self.act_no_list)
        self.list_menu.addAction(self.act_bullet_list)
        self.list_menu.addAction(self.act_numbered_list)
        self.list_menu.addAction(self.act_roman_list)
        self.list_menu.addAction(self.act_uppercase_list)
        self.list_menu.addAction(self.act_lowercase_list)
        self.list_menu.addSeparator()
        self.list_menu.addAction(self.act_increase_indent)
        self.list_menu.addAction(self.act_decrease_indent)

        self.btn_list.setMenu(self.list_menu)

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/widget/text_editor.qss")
        stylesheet.set_style_sheet(self.icon_frame,
                                   ":/StyleSheet/Widget/style-sheet/widget/widget/text_editor_button_frame.qss")

        # Superscript button text
        text = QTextDocument()
        text.setHtml("<p style = color:#484848 >X<sup>&thinsp;2</sup></p>")

        pixmap = self.draw_text(text)
        icon = QIcon(pixmap)
        self.btn_superscript.setIcon(icon)
        self.btn_superscript.setIconSize(pixmap.rect().size() / self.devicePixelRatioF())

        # Subscript button text
        text = QTextDocument()
        text.setHtml("<p style = color:#484848 >X<sub>&thinsp;2</sub></p>")

        pixmap = self.draw_text(text)
        icon = QIcon(pixmap)
        self.btn_subscript.setIcon(icon)
        self.btn_subscript.setIconSize(pixmap.rect().size() / self.devicePixelRatioF())

        # Default color icons
        self.change_highlight_button_icon(self.act_clear_highlight)
        self.change_text_color_button_icon(self.act_black_text)
        self.change_list_button_icon(self.act_no_list)

        # Set visible components and event filter
        self.icon_frame.setVisible(False)
        self.txt_title.installEventFilter(self)
        self.txt_body.installEventFilter(self)
        self.txt_description.setVisible(False)

    def init_connection(self):
        self.btn_bold.clicked.connect(self.format_bold)
        self.btn_italic.clicked.connect(self.format_italic)
        self.btn_underline.clicked.connect(self.format_underline)
        self.btn_strikethrough.clicked.connect(self.format_strikethrough)
        self.btn_superscript.clicked.connect(self.format_superscript)
        self.btn_subscript.clicked.connect(self.format_subscript)
        self.highlight_menu.triggered.connect(self.change_highlight_button_icon)
        self.color_menu.triggered.connect(self.change_text_color_button_icon)
        self.list_menu.triggered.connect(self.change_list_button_icon)
        self.list_menu.triggered.connect(self.format_list)
        self.color_menu.triggered.connect(self.format_text_color)
        self.highlight_menu.triggered.connect(self.format_highlight)
        self.style_menu.triggered.connect(self.format_style)
        self.txt_body.cursorPositionChanged.connect(self.update_button)
        self.txt_width.textEdited.connect(self.update_height)
        self.txt_height.textEdited.connect(self.update_width)
        self.txt_width.editingFinished.connect(self.update_image_size)

    def update_height(self):
        """ Update height value when the width is changed """
        if self.txt_width.text():
            self.txt_height.setText("{:.0f}".format(int(self.txt_width.text()) * 1/self.width_height_ratio))
        else:
            self.txt_height.setText("0")

    def update_width(self):
        """ Update width value when the height is changed """
        if self.txt_height.text():
            self.txt_width.setText("{:.0f}".format(int(self.txt_height.text()) * self.width_height_ratio))
        else:
            self.txt_width.setText("0")

    def update_image_size(self):
        cursor = self.txt_body.textCursor()

        if not cursor.hasSelection():
            cursor.setPosition(self.txt_body.textCursor().position() - 1)
            cursor.setPosition(self.txt_body.textCursor().position(), QTextCursor.KeepAnchor)

        fmt = cursor.charFormat().toImageFormat()
        fmt.setWidth(int(self.txt_width.text()))
        fmt.setHeight(int(self.txt_height.text()))
        cursor.setCharFormat(fmt)
        self.txt_body.setTextCursor(cursor)

    def eventFilter(self, object, event):
        if event.type() == QEvent.FocusIn:
            if object == self.txt_title:
                self.edit_title()
            if object == self.txt_body:
                self.edit_body()
        return QWidget.eventFilter(self, object, event)

    def edit_title(self):
        """ Show the interface element required to edit title """
        self.icon_frame.setVisible(False)
        self.txt_description.setVisible(True)
        self.txt_key.setVisible(True)

    def edit_body(self):
        """ Show the interface element required to edit the body """
        self.icon_frame.setVisible(True)
        self.txt_description.setVisible(False)
        self.txt_key.setVisible(False)

    def change_list_button_icon(self, action):
        """Change the list button icon to the selected list format

        :param action: Selected action.
        :type action: QAction
        """

        # Ignore the indent change action when changing the icon type
        if not (action == self.act_increase_indent or action == self.act_decrease_indent):
            if action == self.act_bullet_list:
                icon = self.draw_list(["•", "•", "•"])
            elif action == self.act_numbered_list:
                icon = self.draw_list(["1.", "2.", "3."])
            elif action == self.act_roman_list:
                icon = self.draw_list(["I.", "II.", "III."])
            elif action == self.act_uppercase_list:
                icon = self.draw_list(["A.", "B.", "C."])
            else:
                icon = self.draw_list(["a.", "b.", "c."])
            self.btn_list.setIcon(icon)

            # Do no check the button is no list is selected
            if not (action == self.act_no_list):
                self.btn_list.setChecked(True)
            elif action == self.act_no_list:
                self.btn_list.setChecked(False)

    def draw_list(self, separator_list):
        """Draw the list icons for the icon menu

        .. note::
            This function handle HiDPI as well a regular screen

        :param separator_list: List of the bullets
        :type separator_list: List[str]
        :returns:  QPixmap -- Icon pixmap
        """
        # Create a base pixmap
        # Set the pixmap pixel ratio so that the image looks good in normal as well as HiDPI screens
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(16 * dpr, 16 * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)  # Required to create a transparent background

        # Paint the elements of the icon
        painter = QPainter(pixmap)
        painter.setFont(QFont(self.font().family(), 5, 50))
        pen = QPen(QColor(72, 72, 72), 1)
        painter.setPen(pen)
        painter.drawLine(7, 3, 15, 3)
        painter.drawText(0, 0, 32, 22, Qt.AlignLeft, separator_list[0])
        painter.drawLine(7, 8, 15, 8)
        painter.drawText(0, 5, 32, 22, Qt.AlignLeft, separator_list[1])
        painter.drawLine(7, 13, 15, 13)
        painter.drawText(0, 10, 32, 22, Qt.AlignLeft, separator_list[2])
        painter.end()

        return QIcon(pixmap)

    def change_text_color_button_icon(self, action):
        """Change the text color button icon to the selected color

        :param action: Selected action.
        :type action: QAction
        """
        if action == self.act_gray_text:
            icon = self.draw_color(common.TEXT_COLOR['gray'].color, common.TEXT_COLOR['gray'].dark_shade)
        elif action == self.act_red_text:
            icon = self.draw_color(common.TEXT_COLOR['red'].color, common.TEXT_COLOR['red'].dark_shade)
        elif action == self.act_orange_text:
            icon = self.draw_color(common.TEXT_COLOR['orange'].color, common.TEXT_COLOR['orange'].dark_shade)
        elif action == self.act_yellow_text:
            icon = self.draw_color(common.TEXT_COLOR['yellow'].color, common.TEXT_COLOR['yellow'].dark_shade)
        elif action == self.act_green_text:
            icon = self.draw_color(common.TEXT_COLOR['green'].color, common.TEXT_COLOR['green'].dark_shade)
        elif action == self.act_blue_text:
            icon = self.draw_color(common.TEXT_COLOR['blue'].color, common.TEXT_COLOR['blue'].dark_shade)
        elif action == self.act_purple_text:
            icon = self.draw_color(common.TEXT_COLOR['purple'].color, common.TEXT_COLOR['purple'].dark_shade)
        else:
            icon = self.draw_color(common.TEXT_COLOR['black'].color, common.TEXT_COLOR['black'].dark_shade)
        self.btn_color.setIcon(icon)

    def change_highlight_button_icon(self, action):
        """Change the highlight button icon to the selected color

        :param action: Selected action.
        :type action: QAction
        """
        if action == self.act_red_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['red'].color, common.HIGHLIGHT_COLOR['red'].dark_shade)
        elif action == self.act_orange_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['orange'].color, common.HIGHLIGHT_COLOR['orange'].dark_shade)
        elif action == self.act_yellow_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['yellow'].color, common.HIGHLIGHT_COLOR['yellow'].dark_shade)
        elif action == self.act_green_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['green'].color, common.HIGHLIGHT_COLOR['green'].dark_shade)
        elif action == self.act_blue_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['blue'].color, common.HIGHLIGHT_COLOR['blue'].dark_shade)
        elif action == self.act_purple_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['purple'].color, common.HIGHLIGHT_COLOR['purple'].dark_shade)
        elif action == self.act_gray_highlight:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['gray'].color, common.HIGHLIGHT_COLOR['gray'].dark_shade)
        else:
            icon = self.draw_color(common.HIGHLIGHT_COLOR['clear'].color, common.HIGHLIGHT_COLOR['clear'].dark_shade)
        self.btn_highlight.setIcon(icon)

    def draw_color(self, fill, border):
        """Draw the color icons for the highlight and the text color menu

        :param fill: Fill color.
        :type fill: QColor
        :param border: Border color.
        :type border: QColor
        :returns:  QPixmap -- Icon pixmap
        """
        # Create a base pixmap
        # Set the pixmap pixel ratio so that the image looks good in normal as well as HiDPI screens
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(16 * dpr, 16 * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)

        # Paint the elements of the icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, 12, 12), 2, 2)

        pen = QPen(border, 1)
        painter.setPen(pen)
        painter.fillPath(path, fill)
        painter.drawPath(path)
        painter.end()

        return QIcon(pixmap)

    def draw_text(self, text):
        """Draw an icon from a html text and return it as a pixmap.

        .. note::
            This function handle HiDPI as well a regular screen.

        :param text: QTextDocument with HTML code for the icon.
        :type text: QTextDocument
        :returns:  QPixmap -- Returns pixmap that can be used to create the icon

        .. note::
            Unlike the other drawing function, this function return a pixel map. As of now, this is required to create
            a good sized icon. This should therefore not be changed unless the the output icon size is right (it is
            currently too small).
        """
        # Create a base pixmap
        # Set the pixmap pixel ratio so that the image looks good in normal as well as HiDPI screens
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(text.size().width() * dpr, text.size().height() * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)

        # Paint the elements of the icon
        painter = QPainter(pixmap)
        text.drawContents(painter, QRectF(pixmap.rect()))
        painter.end()

        return pixmap

    def merge_format_on_word_or_selection(self, fmt):
        """ Change the caracter format when a format button is pressed.

        The font is changed for the selection or from the cursor position.
        :param fmt: Text format
        """
        cursor = self.txt_body.textCursor()
        cursor.mergeCharFormat(fmt)
        self.txt_body.mergeCurrentCharFormat(fmt)

    def format_bold(self):
        """ Set text format to bold. """
        fmt = QTextCharFormat()
        if self.btn_bold.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_italic(self):
        """ Set text format to italic. """
        fmt = QTextCharFormat()
        if self.btn_italic.isChecked():
            fmt.setFontItalic(True)
        else:
            fmt.setFontItalic(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_underline(self):
        """ Set text format to underline. """
        fmt = QTextCharFormat()
        if self.btn_underline.isChecked():
            fmt.setFontUnderline(True)
        else:
            fmt.setFontUnderline(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_strikethrough(self):
        """ Set text format to strikethrough. """
        fmt = QTextCharFormat()
        if self.btn_strikethrough.isChecked():
            fmt.setFontStrikeOut(True)
        else:
            fmt.setFontStrikeOut(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_superscript(self):
        """ Set text vertical alignment to superscript. """
        fmt = QTextCharFormat()
        if self.btn_superscript.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_subscript(self):
        """ Set text vertical alignment to subscript. """
        fmt = QTextCharFormat()
        if self.btn_subscript.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_list(self, action):
        """ set list format according to selected format

        :param action: Selected action.
        :type action: QAction
        """

        # Create a new list
        if not (action == self.act_increase_indent or action == self.act_decrease_indent or action == self.act_no_list):
            # Set the list type format
            fmt = QTextListFormat()
            if action == self.act_bullet_list:
                fmt.setStyle(QTextListFormat.ListDisc)
            elif action == self.act_numbered_list:
                fmt.setStyle(QTextListFormat.ListDecimal)
            elif action == self.act_roman_list:
                fmt.setStyle(QTextListFormat.ListUpperRoman)
            elif action == self.act_uppercase_list:
                fmt.setStyle(QTextListFormat.ListUpperAlpha)
            else:
                fmt.setStyle(QTextListFormat.ListLowerAlpha)

            # Add the list to the the text edit
            cursor = self.txt_body.textCursor()
            cursor.createList(fmt)
        # Delete an existing list
        elif action == self.act_no_list:
            # Get the current list
            cursor = self.txt_body.textCursor()
            current_list = cursor.currentList()
            current_block = cursor.block()

            # Remove the list
            current_list.remove(current_block)

            # Restore indent
            fmt = cursor.blockFormat()
            fmt.setIndent(0)
            cursor.setBlockFormat(fmt)
        # Change the indent
        else:
            cursor = self.txt_body.textCursor()
            current_format = cursor.currentList().format()
            current_indent = current_format.indent()

            if action == self.act_increase_indent:
                new_indent = current_indent + 1
            else:
                new_indent = current_indent - 1

            new_format = current_format
            new_format.setIndent(new_indent)
            cursor.createList(new_format)

    def format_text_color(self, action):
        """ Set the text color

        :param action: Selected action.
        :type action: QAction
        """
        if action == self.act_gray_text:
            text_color = QColor(196, 196, 196)
        elif action == self.act_red_text:
            text_color = QColor(150, 16, 16)
        elif action == self.act_orange_text:
            text_color = QColor(211, 116, 0)
        elif action == self.act_yellow_text:
            text_color = QColor(229, 221, 0)
        elif action == self.act_green_text:
            text_color = QColor(34, 139, 34)
        elif action == self.act_blue_text:
            text_color = QColor(18, 18, 130)
        elif action == self.act_purple_text:
            text_color = QColor(117, 21, 117)
        else:
            text_color = Qt.black

        fmt = QTextCharFormat()
        fmt.setForeground(QBrush(text_color))
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_highlight(self, action):
        """ Set the highlight color

        .. note::
            The highlight color alpha channel is set to 128 so the color are semi-transparent. This prevent the colors
            to be too harsh.

        :param action: Selected action.
        :type action: QAction
        """
        fmt = QTextCharFormat()

        # Set the selected color to background
        if not action == self.act_clear_highlight:
            if action == self.act_red_highlight:
                highlight_color = QColor(242, 41, 74, 128)
            elif action == self.act_orange_highlight:
                highlight_color = QColor(252, 116, 42, 128)
            elif action == self.act_yellow_highlight:
                highlight_color = QColor(255, 251, 45, 128)
            elif action == self.act_green_highlight:
                highlight_color = QColor(0, 250, 154, 128)
            elif action == self.act_blue_highlight:
                highlight_color = QColor(49, 170, 226, 128)
            elif action == self.act_purple_highlight:
                highlight_color = QColor(155, 71, 229, 128)
            else:
                highlight_color = QColor(196, 196, 196, 128)

            fmt.setBackground(QBrush(highlight_color))
        # Remove the background
        else:
            fmt.setBackground(QBrush(Qt.white))
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_style(self, action):
        """ Set a predefined format on the selected text

        :param action: Selected action (format).
        :type action: QAction
        """
        fmt = QTextCharFormat()

        # Define the format according to the selected style
        if action == self.act_part:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(20)
        elif action == self.act_section:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(16)
        elif action == self.act_subsection:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(14)
        elif action == self.act_subsubsection:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(12)
        elif action == self.act_body:
            fmt.setFontWeight(50)
            fmt.setFontPointSize(12)
        elif action == self.act_note:
            fmt.setFontWeight(50)
            fmt.setFontPointSize(10)

        # Define the format common to every style
        fmt.setForeground(QBrush(Qt.black))
        fmt.setBackground(QBrush(Qt.white))
        fmt.setFontItalic(False)
        fmt.setFontUnderline(False)
        fmt.setFontStrikeOut(False)
        fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)

        self.merge_format_on_word_or_selection(fmt=fmt)

    def update_button(self):
        """ Set the button states to match the selected text format """

        # Get text format
        cfmt = self.txt_body.textCursor().charFormat()

        # Bold button
        if cfmt.fontWeight() == 75:
            self.btn_bold.setChecked(True)
        else:
            self.btn_bold.setChecked(False)

        # Italic button
        if cfmt.fontItalic():
            self.btn_italic.setChecked(True)
        else:
            self.btn_italic.setChecked(False)

        # Underline button
        if cfmt.fontUnderline():
            self.btn_underline.setChecked(True)
        else:
            self.btn_underline.setChecked(False)

        # Strikethrough button
        if cfmt.fontStrikeOut():
            self.btn_strikethrough.setChecked(True)
        else:
            self.btn_strikethrough.setChecked(False)

        # Superscript button
        if cfmt.verticalAlignment() == QTextCharFormat.AlignSuperScript:
            self.btn_superscript.setChecked(True)
        else:
            self.btn_superscript.setChecked(False)

        # Subscript button
        if cfmt.verticalAlignment() == QTextCharFormat.AlignSubScript:
            self.btn_subscript.setChecked(True)
        else:
            self.btn_subscript.setChecked(False)

        # Get color format
        # Background color
        background_color = cfmt.background().color()
        if background_color.rgb() == common.HIGHLIGHT_COLOR['red'].color.rgb():
            self.change_highlight_button_icon(self.act_red_highlight)
        elif background_color.rgb() == common.HIGHLIGHT_COLOR['orange'].color.rgb():
            self.change_highlight_button_icon(self.act_orange_highlight)
        elif background_color.rgb() == common.HIGHLIGHT_COLOR['yellow'].color.rgb():
            self.change_highlight_button_icon(self.act_yellow_highlight)
        elif background_color.rgb() == common.HIGHLIGHT_COLOR['green'].color.rgb():
            self.change_highlight_button_icon(self.act_green_highlight)
        elif background_color.rgb() == common.HIGHLIGHT_COLOR['blue'].color.rgb():
            self.change_highlight_button_icon(self.act_blue_highlight)
        elif background_color.rgb() == common.HIGHLIGHT_COLOR['purple'].color.rgb():
            self.change_highlight_button_icon(self.act_purple_highlight)
        elif background_color.rgb() == common.HIGHLIGHT_COLOR['gray'].color.rgb():
            self.change_highlight_button_icon(self.act_gray_highlight)
        else:
            self.change_highlight_button_icon(self.act_clear_highlight)

        # Text color
        text_color = cfmt.foreground().color()

        if text_color == common.TEXT_COLOR['gray'].color:
            self.change_text_color_button_icon(self.act_gray_text)
        elif text_color == common.TEXT_COLOR['red'].color:
            self.change_text_color_button_icon(self.act_red_text)
        elif text_color == common.TEXT_COLOR['orange'].color:
            self.change_text_color_button_icon(self.act_orange_text)
        elif text_color == common.TEXT_COLOR['yellow'].color:
            self.change_text_color_button_icon(self.act_yellow_text)
        elif text_color == common.TEXT_COLOR['gray'].color:
            self.change_text_color_button_icon(self.act_gray_text)
        elif text_color == common.TEXT_COLOR['green'].color:
            self.change_text_color_button_icon(self.act_green_text)
        elif text_color == common.TEXT_COLOR['blue'].color:
            self.change_text_color_button_icon(self.act_blue_text)
        elif text_color == common.TEXT_COLOR['purple'].color:
            self.change_text_color_button_icon(self.act_purple_text)
        else:
            self.change_text_color_button_icon(self.act_black_text)

        # Get list format
        if self.txt_body.textCursor().currentList():
            self.btn_list.setChecked(True)
        else:
            self.btn_list.setChecked(False)

        if self.txt_body.is_image():
            fmt = self.txt_body.textCursor().charFormat().toImageFormat()
            self.txt_height.setText("{:d}".format(int(fmt.height())))
            self.txt_width.setText("{:d}".format(int(fmt.width())))
            self.width_height_ratio = fmt.width() / fmt.height()
            self.txt_width.setEnabled(True)
            self.txt_height.setEnabled(True)
        else:
            self.txt_width.setEnabled(False)
            self.txt_height.setEnabled(False)


class ProtocolTextEditor(TextEditor):
    def __init__(self, editor_type, tag_list, reference_list):
        super(ProtocolTextEditor, self).__init__(editor_type=editor_type, tag_list=tag_list, reference_list=reference_list)
        self.txt_key.setPlaceholderText("Protocol key")
        self.txt_description.setPlaceholderText("Description of the protocol")
        self.txt_title.setPlaceholderText("Untitled protocol")


class ExperimentTextEditor(TextEditor):
    def __init__(self, tag_list, reference_list, dataset_list, protocol_list, key_list):
        super(ExperimentTextEditor, self).__init__(common.TYPE_EXPERIMENT, tag_list=tag_list,
                                                   reference_list=reference_list,
                                                   dataset_list=dataset_list, protocol_list=protocol_list)

        completer = QCompleter(key_list)
        self.txt_key.setCompleter(completer)

        # Remove the save button
        self.btn_save.deleteLater()
        sip.delete(self.save_layout)
