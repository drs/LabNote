"""
This module contain the classes responsible for launching and managing the library dialog.
"""

# Python import
import sip

# PyQt import
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QTextEdit, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Project import
from labnote.ui.ui_library import Ui_Library
from labnote.core import stylesheet


class Library(QDialog, Ui_Library):
    """
    Class responsible of managing the library window interface.
    """

    # Class variable
    grid_layout = None

    def __init__(self, parent=None):
        super(Library, self).__init__(parent)
        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()

        # Show the dialog
        self.show()

    def init_ui(self):
        self.setWindowTitle("LabNote - Library")
        self.setSizeGripEnabled(True)

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/library.qss")

        # Remove focus rectangle
        self.treeview.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.txt_key.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.txt_search.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Key size
        self.lbl_key.setFixedSize(102, 21)

        # Show the article fields
        self.article_field()

        # Create the manage button menu
        manage_menu = QMenu(self)
        manage_menu.setFont(QFont(self.font().family(), 13, QFont.Normal))
        act_create_category = QAction("Create category", self)
        manage_menu.addAction(act_create_category)
        act_rename_category = QAction("Rename category", self)
        manage_menu.addAction(act_rename_category)
        act_delete_category = QAction("Delete category", self)
        manage_menu.addAction(act_delete_category)
        manage_menu.addSeparator()
        act_create_subcategory = QAction("Create subcategory", self)
        manage_menu.addAction(act_create_subcategory)
        act_rename_subcategory = QAction("Rename subcategory", self)
        manage_menu.addAction(act_rename_subcategory)
        act_delete_subcategory = QAction("Delete subcategory", self)
        manage_menu.addAction(act_delete_subcategory)
        self.btn_manage.setMenu(manage_menu)

        # Connect slots
        self.comboBox.currentTextChanged.connect(self.show_field)

    def create_grid(self):
        """ Create the grid layout

        :return QGridLayout: Grid Layout
        """
        self.grid_layout = QGridLayout()
        self.grid_layout.setColumnMinimumWidth(0, 110)
        self.grid_layout.setSpacing(2)

    def prepare_grid(self):
        """ Delete the grid layout """
        self.delete_layout(self.grid_layout)
        self.create_grid()

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

    def show_field(self, text):
        """ Show the field related to a specific type of literature """
        print(text)
        if text == "Article":
            self.article_field()
        elif text == "Book":
            self.book_field()
        else:
            self.chapter_field()

    def article_field(self):
        """ Show all the article related fields in the layout """
        self.prepare_grid()

        lbl_author = QLabel("Author")
        lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_author, 0, 0)
        txt_author = QLineEdit()
        txt_author.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_author, 0, 1)
        lbl_title = QLabel("Title")
        lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_title, 1, 0)
        txt_title = QLineEdit()
        txt_title.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_title, 1, 1)
        lbl_journal = QLabel("Journal")
        lbl_journal.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_journal, 2, 0)
        txt_journal = QLineEdit()
        txt_journal.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_journal, 2, 1)
        lbl_year = QLabel("Year")
        lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_year, 3, 0)
        txt_year = QLineEdit()
        txt_year.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_year, 3, 1)
        lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(lbl_volume, 4, 0)
        txt_volume = QLineEdit()
        txt_volume.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_volume, 4, 1)
        lbl_issue = QLabel("Issue")
        self.grid_layout.addWidget(lbl_issue, 5, 0)
        txt_issue = QLineEdit()
        txt_issue.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_issue, 5, 1)
        lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(lbl_pages, 6, 0)
        txt_pages = QLineEdit()
        txt_pages.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_pages, 6, 1)
        lbl_description = QLabel("Description")
        lbl_description.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.addWidget(lbl_description, 7, 0)
        txt_description = QTextEdit()
        self.grid_layout.addWidget(txt_description, 7, 1)
        lbl_abstract = QLabel("Abstract")
        lbl_abstract.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.addWidget(lbl_abstract, 8, 0)
        txt_abstract = QTextEdit()
        self.grid_layout.addWidget(txt_abstract, 8, 1)

        self.detail_layout.addLayout(self.grid_layout, 1)

    def book_field(self):
        """ Show all the book related fields in the layout """
        self.prepare_grid()

        lbl_author = QLabel("Author")
        lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_author, 0, 0)
        txt_author = QLineEdit()
        txt_author.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_author, 0, 1)
        lbl_title = QLabel("Title")
        lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_title, 1, 0)
        txt_title = QLineEdit()
        txt_title.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_title, 1, 1)
        lbl_year = QLabel("Year")
        lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_year, 2, 0)
        txt_year = QLineEdit()
        txt_year.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_year, 2, 1)
        lbl_publisher = QLabel("Publisher")
        lbl_publisher.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_publisher, 3, 0)
        txt_publisher = QLineEdit()
        txt_publisher.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_publisher, 3, 1)
        lbl_place_published = QLabel("Place published")
        self.grid_layout.addWidget(lbl_place_published, 4, 0)
        txt_place_published = QLineEdit()
        txt_place_published.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_place_published, 4, 1)
        lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(lbl_volume, 5, 0)
        txt_volume = QLineEdit()
        txt_volume.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_volume, 5, 1)
        lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(lbl_pages, 6, 0)
        txt_pages = QLineEdit()
        txt_pages.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_pages, 6, 1)
        lbl_edition = QLabel("Edition")
        self.grid_layout.addWidget(lbl_edition, 7, 0)
        txt_edition = QLineEdit()
        txt_edition.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_edition, 7, 1)
        lbl_description = QLabel("Description")
        self.grid_layout.addWidget(lbl_description, 8, 0)
        txt_description = QTextEdit()
        self.grid_layout.addWidget(txt_description, 8, 1)
        lbl_abstract = QLabel("Abstract")
        self.grid_layout.addWidget(lbl_abstract, 9, 0)
        txt_abstract = QTextEdit()
        self.grid_layout.addWidget(txt_abstract, 9, 1)

        self.detail_layout.addLayout(self.grid_layout, 1)

    def chapter_field(self):
        """ Show all the chapter related fields in the layout """
        self.prepare_grid()

        lbl_author = QLabel("Author")
        lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_author, 0, 0)
        txt_author = QLineEdit()
        txt_author.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_author, 0, 1)
        lbl_chapter = QLabel("Chapter")
        lbl_chapter.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_chapter, 1, 0)
        txt_chapter = QLineEdit()
        txt_chapter.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_chapter, 1, 1)
        lbl_title = QLabel("Book title")
        lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_title, 2, 0)
        txt_title = QLineEdit()
        txt_title.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_title, 2, 1)
        lbl_year = QLabel("Year")
        lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(lbl_year, 3, 0)
        txt_year = QLineEdit()
        txt_year.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_year, 3, 1)
        lbl_editor = QLabel("Editor")
        self.grid_layout.addWidget(lbl_editor, 4, 0)
        txt_editor = QLineEdit()
        txt_editor.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_editor, 4, 1)
        lbl_publisher = QLabel("Publisher")
        self.grid_layout.addWidget(lbl_publisher, 5, 0)
        txt_publisher = QLineEdit()
        txt_publisher.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_publisher, 5, 1)
        lbl_place_published = QLabel("Place published")
        self.grid_layout.addWidget(lbl_place_published, 6, 0)
        txt_place_published = QLineEdit()
        txt_place_published.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_place_published, 6, 1)
        lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(lbl_volume, 7, 0)
        txt_volume = QLineEdit()
        txt_volume.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_volume, 7, 1)
        lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(lbl_pages, 8, 0)
        txt_pages = QLineEdit()
        txt_pages.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_pages, 8, 1)
        lbl_edition = QLabel("Edition")
        self.grid_layout.addWidget(lbl_edition, 9, 0)
        txt_edition = QLineEdit()
        txt_edition.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.grid_layout.addWidget(txt_edition, 9, 1)
        lbl_description = QLabel("Description")
        self.grid_layout.addWidget(lbl_description, 10, 0)
        txt_description = QTextEdit()
        self.grid_layout.addWidget(txt_description, 10, 1)
        lbl_abstract = QLabel("Abstract")
        self.grid_layout.addWidget(lbl_abstract, 11, 0)
        txt_abstract = QTextEdit()
        self.grid_layout.addWidget(txt_abstract, 11, 1)

        self.detail_layout.addLayout(self.grid_layout, 1)
