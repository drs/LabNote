"""
This module contain the classes responsible for launching and managing the library dialog.
"""

# Python import
import sip
import sqlite3
import uuid
import os

# PyQt import
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QMessageBox, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, QFileInfo, QItemSelectionModel
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QPen, QBrush

# Project import
from labnote.ui.ui_library import Ui_Library
from labnote.core import stylesheet, sqlite_error, data, common
from labnote.interface.widget.textedit import CompleterTextEdit, PlainTextEdit
from labnote.utils import database, fsentry, directory
from labnote.interface.widget.lineedit import LineEdit, NumberLineEdit, YearLineEdit, PagesLineEdit, SearchLineEdit
from labnote.interface.widget.widget import CategoryFrame
from labnote.interface.widget import widget
from labnote.interface.widget.object import KeyValidator


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


class Library(QDialog, Ui_Library):
    """
    Class responsible of managing the library window interface.
    """

    # Class variable
    grid_layout = None
    creating_reference = False  # True when a new reference is created
    tag_list = []

    # Signals definition
    pdf_added = pyqtSignal(str)
    pdf_deleted = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, tag_list, parent=None):
        super(Library, self).__init__(parent)
        # Initialize global variable
        self.tag_list = tag_list

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Show the widget content
        self.category_frame.show_list()

        # Show the dialog
        self.show()

    def init_ui(self):
        self.setWindowTitle("LabNote - Library")
        self.setSizeGripEnabled(True)
        self.read_settings()

        # Add the search LineEdit
        self.txt_search = SearchLineEdit()
        self.layout_title.insertWidget(3, self.txt_search)

        # Create the category frame
        self.category_frame = CategoryFrame('Bookshelf', widget.TYPE_LIBRARY)
        self.main_frame.layout().insertWidget(0, self.category_frame)

        # Create the pdf widget
        self.pdf_box = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 60, 20, 60)
        self.pdf_widget = PDFWidget()
        layout.addWidget(self.pdf_widget)
        self.pdf_box.setLayout(layout)
        self.pdf_box.setFixedWidth(180)
        self.main_frame.layout().addWidget(self.pdf_box)

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/library.qss")

        # Remove focus rectangle
        self.txt_key.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Key size
        self.lbl_key.setFixedSize(102, 21)

        # Clear the form
        self.clear_form()

        # Key validator
        self.txt_key.setValidator(KeyValidator())

        # Focus policy
        self.txt_search.setFocusPolicy(self.txt_search.focusPolicy() ^ Qt.TabFocus)
        self.category_frame.view_tree.setFocusPolicy(self.category_frame.view_tree.focusPolicy()
                                                     ^ Qt.TabFocus)

    def init_connection(self):
        self.comboBox.currentTextChanged.connect(self.show_field)
        self.category_frame.btn_add.clicked.connect(self.start_creating_reference)
        self.btn_save.clicked.connect(self.process_reference)
        self.category_frame.view_tree.collapsed.connect(self.save_treeview_state)
        self.category_frame.view_tree.expanded.connect(self.save_treeview_state)
        self.category_frame.view_tree.drop_finished.connect(self.drop_finished)
        self.pdf_widget.pdf_dropped.connect(self.add_pdf)
        self.pdf_widget.delete.connect(self.remove_pdf)
        self.pdf_added.connect(self.pdf_widget.show_pdf)
        self.pdf_deleted.connect(self.pdf_widget.remove_pdf)
        self.category_frame.delete.connect(self.delete_reference)
        self.category_frame.list_displayed.connect(self.restore_treeview_state)
        self.category_frame.entry_selected.connect(self.show_reference_details)
        self.category_frame.selection_changed.connect(self.clear_form)
        self.txt_key.textChanged.connect(self.set_modified)

    def get_tag_list(self):
        """ Get the list of all tag """
        tag_list = []

        try:
            tag_list = database.select_tag_list()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to get tag list",
                                  "An error occurred while getting the tag list.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.tag_list = tag_list

    def add_pdf(self, file):
        """ Add a PDF to a reference

        :param file: PDF file URL
        :type file: str
        """
        ref_uuid = self.category_frame.get_user_data()

        try:
            reference_file = fsentry.add_reference_pdf(ref_uuid=ref_uuid, file=file)
        except (sqlite3.Error, OSError) as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to save reference",
                                  "An error occurred while saving the reference PDF.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.pdf_added.emit(reference_file)

    def remove_pdf(self):
        """ Remove the PDF from the database and file structure """
        ref_uuid = self.category_frame.get_user_data()
        try:
            fsentry.delete_reference_pdf(ref_uuid=ref_uuid)
        except (sqlite3.Error, OSError) as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to delete reference",
                                  "An error occurred while deleting the reference PDF.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.pdf_deleted.emit()

    def drop_finished(self, index):
        """ Update an item information after a drag and drop mouvement """
        category = self.category_frame.get_category(index)
        subcategory = self.category_frame.get_subcategory(index)

        try:
            database.update_reference_category(self.category_frame.view_tree.selectedIndexes()[0].data(Qt.UserRole),
                                               category, subcategory)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the reference data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.category_frame.show_list()

    def show_reference_details(self, ref_uuid):
        """ Show a reference details when it is selected """
        try:
            reference = database.select_reference(ref_uuid)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the reference data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.enable_all(True)

        # Show the fields
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
            self.txt_abstract.setPlainText(data.receive_string(reference['abstract']))
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
            self.txt_abstract.setPlainText(data.receive_string(reference['abstract']))
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
            self.txt_abstract.setPlainText(data.receive_string(reference['abstract']))

        # Show the PDF file
        if reference['file']:
            file = os.path.join(directory.REFERENCES_DIRECTORY_PATH + "/{}".format(uuid))
            self.pdf_widget.show_pdf(file=file)

    def start_creating_reference(self):
        """ Enable new reference creation """
        if self.category_frame.get_current_level() == LEVEL_CATEGORY or \
                self.category_frame.get_current_level() == LEVEL_SUBCATEGORY or \
                self.category_frame.get_current_level() == LEVEL_ENTRY:
            self.clear_form()
            self.creating_reference = True
            self.enable_all(True)
            self.pdf_widget.clear_form()
            self.pdf_widget.setEnabled(False)

    def clear_form(self):
        """ Clear all data in the form """
        self.creating_reference = False
        self.txt_key.clear()
        self.article_field()
        self.enable_all(False)
        self.pdf_widget.clear_form()

    def delete_reference(self, ref_uuid):
        """ Delete a reference """
        try:
            fsentry.delete_reference(ref_uuid=ref_uuid)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to delete reference",
                                  "An error occurred while deleting the reference.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return
        self.category_frame.show_list()
        self.clear_form()

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
        self.pdf_widget.setEnabled(enable)

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
            # Get the current item data
            index = self.category_frame.view_tree.selectionModel().currentIndex()
            category_id = self.category_frame.get_category(index)
            subcategory_id = self.category_frame.get_subcategory(index)

            if category_id:
                ref_type = self.comboBox.currentText()
                anchor = self.txt_description.anchors()

                if ref_type == "Article":
                    author = data.prepare_string(self.txt_author.text())
                    title = data.prepare_string(self.txt_title.text())
                    journal = data.prepare_string(self.txt_journal.text())
                    year = data.prepare_string_number(self.txt_year.text())
                    volume = data.prepare_string_number(self.txt_volume.text())
                    issue = data.prepare_string_number(self.txt_issue.text())
                    pages = data.prepare_string(self.txt_pages.text())
                    description = data.prepare_textedit(self.txt_description)
                    abstract = data.prepare_string(self.txt_abstract.toPlainText())
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
                    abstract = data.prepare_string(self.txt_abstract.toPlainText())
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
                    abstract = data.prepare_string(self.txt_abstract.toPlainText())

                if self.creating_reference:
                    ref_uuid = data.uuid_bytes(uuid.uuid4())
                    try:
                        if ref_type == "Article":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, ref_type=TYPE_ARTICLE,
                                                category_id=category_id, subcategory_id=subcategory_id, author=author,
                                                title=title, journal=journal, year=year, volume=volume, issue=issue,
                                                pages=pages, description=description, abstract=abstract,
                                                tag_list=anchor['tag'])
                        elif ref_type == "Book":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=category_id,
                                                subcategory_id=subcategory_id, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                ref_type=TYPE_BOOK, tag_list=anchor['tag'])
                        elif ref_type == "Chapter":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=category_id,
                                                subcategory_id=subcategory_id, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                chapter=chapter, editor=editor, ref_type=TYPE_CHAPTER,
                                                tag_list=anchor['tag'])
                        self.done_modifing_reference(ref_uuid=data.uuid_string(ref_uuid))
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
                    ref_uuid = data.uuid_bytes(self.category_frame.get_user_data())
                    try:
                        if ref_type == "Article":
                            database.update_ref(ref_uuid=ref_uuid, ref_key=key, ref_type=TYPE_ARTICLE, author=author,
                                                title=title, journal=journal, year=year, volume=volume, issue=issue,
                                                pages=pages, description=description, abstract=abstract,
                                                tag_list=anchor['tag'])
                        elif ref_type == "Book":
                            database.update_ref(ref_uuid=ref_uuid, ref_key=key, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                ref_type=TYPE_BOOK, tag_list=anchor['tag'])
                        elif ref_type == "Chapter":
                            database.update_ref(ref_uuid=ref_uuid, ref_key=key, author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                chapter=chapter, editor=editor, ref_type=TYPE_CHAPTER,
                                                tag_list=anchor['tag'])
                        self.done_modifing_reference(ref_uuid=ref_uuid)
                    except sqlite3.Error as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to update reference")
                            message.setInformativeText("The reference key must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to update reference")
                            message.setInformativeText("The reference key must be unique.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to update reference",
                                                  "An error occurred while updating the reference.", QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return

    def done_modifing_reference(self, ref_uuid):
        """ Active the interface element after the reference is saved """
        self.category_frame.show_list()

        model = self.category_frame.view_tree.model()
        match = model.match(model.index(0, 0), Qt.UserRole, ref_uuid, 1, Qt.MatchRecursive)
        if match:
            self.category_frame.view_tree.selectionModel().setCurrentIndex(match[0], QItemSelectionModel.Select)
            self.category_frame.view_tree.repaint()
        self.get_tag_list()
        self.setWindowModified(False)

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

    def set_modified(self):
        """ Set the window state as modified """
        self.setWindowModified(True)

    def article_field(self, fields=None):
        """ Show all the article related fields in the layout """
        self.prepare_grid()

        self.lbl_author = QLabel("Author")
        self.lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_author, 0, 0)
        self.txt_author = LineEdit()
        self.txt_author.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_author, 0, 1)

        self.lbl_title = QLabel("Title")
        self.lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_title, 1, 0)
        self.txt_title = LineEdit()
        self.txt_title.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_title, 1, 1)

        self.lbl_journal = QLabel("Journal")
        self.lbl_journal.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_journal, 2, 0)
        self.txt_journal = LineEdit()
        self.txt_journal.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_journal, 2, 1)

        self.lbl_year = QLabel("Year")
        self.lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_year, 3, 0)
        self.txt_year = YearLineEdit()
        self.txt_year.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_year, 3, 1)

        self.lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(self.lbl_volume, 4, 0)
        self.txt_volume = NumberLineEdit()
        self.txt_volume.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_volume, 4, 1)

        self.lbl_issue = QLabel("Issue")
        self.grid_layout.addWidget(self.lbl_issue, 5, 0)
        self.txt_issue = NumberLineEdit()
        self.txt_issue.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_issue, 5, 1)

        self.lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(self.lbl_pages, 6, 0)
        self.txt_pages = PagesLineEdit()
        self.txt_pages.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_pages, 6, 1)

        self.lbl_description = QLabel("Description")
        self.lbl_description.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.addWidget(self.lbl_description, 7, 0)
        self.txt_description = CompleterTextEdit(self.tag_list)
        self.txt_description.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_description, 7, 1)

        self.lbl_abstract = QLabel("Abstract")
        self.lbl_abstract.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.addWidget(self.lbl_abstract, 8, 0)
        self.txt_abstract = PlainTextEdit()
        self.txt_abstract.textChanged.connect(self.set_modified)
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

    def book_field(self, fields=None):
        """ Show all the book related fields in the layout """
        self.prepare_grid()

        self.lbl_author = QLabel("Author")
        self.lbl_author.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_author, 0, 0)
        self.txt_author = LineEdit()
        self.txt_author.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_author, 0, 1)

        self.lbl_title = QLabel("Title")
        self.lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_title, 1, 0)
        self.txt_title = LineEdit()
        self.txt_title.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_title, 1, 1)

        self.lbl_year = QLabel("Year")
        self.lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_year, 2, 0)
        self.txt_year = YearLineEdit()
        self.txt_year.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_year, 2, 1)

        self.lbl_publisher = QLabel("Publisher")
        self.lbl_publisher.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_publisher, 3, 0)
        self.txt_publisher = LineEdit()
        self.txt_publisher.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_publisher, 3, 1)

        self.lbl_place_published = QLabel("Place published")
        self.grid_layout.addWidget(self.lbl_place_published, 4, 0)
        self.txt_place_published = LineEdit()
        self.txt_place_published.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_place_published, 4, 1)

        self.lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(self.lbl_volume, 5, 0)
        self.txt_volume = NumberLineEdit()
        self.txt_volume.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_volume, 5, 1)

        self.lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(self.lbl_pages, 6, 0)
        self.txt_pages = PagesLineEdit()
        self.txt_pages.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_pages, 6, 1)

        self.lbl_edition = QLabel("Edition")
        self.grid_layout.addWidget(self.lbl_edition, 7, 0)
        self.txt_edition = LineEdit()
        self.txt_edition.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_edition, 7, 1)

        self.lbl_description = QLabel("Description")
        self.grid_layout.addWidget(self.lbl_description, 8, 0)
        self.txt_description = CompleterTextEdit(self.tag_list)
        self.txt_description.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_description, 8, 1)

        self.lbl_abstract = QLabel("Abstract")
        self.grid_layout.addWidget(self.lbl_abstract, 9, 0)
        self.txt_abstract = PlainTextEdit()
        self.txt_abstract.textChanged.connect(self.set_modified)
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
        self.txt_author.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_author, 0, 1)

        self.lbl_chapter = QLabel("Chapter")
        self.lbl_chapter.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_chapter, 1, 0)
        self.txt_chapter = LineEdit()
        self.txt_chapter.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_chapter, 1, 1)

        self.lbl_title = QLabel("Book title")
        self.lbl_title.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_title, 2, 0)
        self.txt_title = LineEdit()
        self.txt_title.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_title, 2, 1)

        self.lbl_year = QLabel("Year")
        self.lbl_year.setFont(QFont(self.font().family(), weight=QFont.Bold))
        self.grid_layout.addWidget(self.lbl_year, 3, 0)
        self.txt_year = YearLineEdit()
        self.txt_year.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_year, 3, 1)

        self.lbl_editor = QLabel("Editor")
        self.grid_layout.addWidget(self.lbl_editor, 4, 0)
        self.txt_editor = LineEdit()
        self.txt_editor.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_editor, 4, 1)

        self.lbl_publisher = QLabel("Publisher")
        self.grid_layout.addWidget(self.lbl_publisher, 5, 0)
        self.txt_publisher = LineEdit()
        self.txt_publisher.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_publisher, 5, 1)

        self.lbl_place_published = QLabel("Place published")
        self.grid_layout.addWidget(self.lbl_place_published, 6, 0)
        self.txt_place_published = LineEdit()
        self.txt_place_published.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_place_published, 6, 1)

        self.lbl_volume = QLabel("Volume")
        self.grid_layout.addWidget(self.lbl_volume, 7, 0)
        self.txt_volume = NumberLineEdit()
        self.txt_volume.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_volume, 7, 1)

        self.lbl_pages = QLabel("Pages")
        self.grid_layout.addWidget(self.lbl_pages, 8, 0)
        self.txt_pages = PagesLineEdit()
        self.txt_pages.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_pages, 8, 1)

        self.lbl_edition = QLabel("Edition")
        self.grid_layout.addWidget(self.lbl_edition, 9, 0)
        self.txt_edition = NumberLineEdit()
        self.txt_edition.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_edition, 9, 1)

        self.lbl_description = QLabel("Description")
        self.grid_layout.addWidget(self.lbl_description, 10, 0)
        self.txt_description = CompleterTextEdit(self.tag_list)
        self.txt_description.textChanged.connect(self.set_modified)
        self.grid_layout.addWidget(self.txt_description, 10, 1)

        self.lbl_abstract = QLabel("Abstract")
        self.grid_layout.addWidget(self.lbl_abstract, 11, 0)
        self.txt_abstract = PlainTextEdit()
        self.txt_abstract.textChanged.connect(self.set_modified)
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

    def closeEvent(self, event):
        self.save_treeview_state()
        self.save_settings()
        self.closed.emit()
        event.accept()

    def save_settings(self):
        """ Save the dialog geometry """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Library")
        settings.setValue("Geometry", self.saveGeometry())
        settings.setValue("Maximized", self.isMaximized())
        settings.endGroup()

    def read_settings(self):
        """ Restore the dialog geometry """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Library")
        self.restoreGeometry(settings.value("Geometry", self.saveGeometry()))
        if settings.value("Maximized", self.isMaximized()):
            self.showMaximized()
        settings.endGroup()

    def save_treeview_state(self):
        """ Save the treeview expanded state """

        # Generate list
        expanded_item = []
        for index in self.category_frame.view_tree.model().get_persistant_index_list():
            if self.category_frame.view_tree.isExpanded(index) and index.data(QT_StateRole):
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

        model = self.category_frame.view_tree.model()

        if expanded_item:
            for item in expanded_item:
                match = model.match(model.index(0, 0), QT_StateRole, item, 1, Qt.MatchRecursive)

                if match:
                    self.category_frame.view_tree.setExpanded(match[0], True)


class PDFWidget(QWidget):
    """ Widget that accept PDF drop """

    # Global variable
    contains_file = False
    file = None

    # Signals
    pdf_dropped = pyqtSignal(str)
    delete = pyqtSignal()

    def __init__(self):
        super(PDFWidget, self).__init__()
        self.init_ui()
        self.init_connection()
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setStyleSheet(self.setStyleSheet(".QWidget { "
                                                "   border: 1.5px dashed rgb(172, 172, 172); "
                                                "   border-radius: 5px"
                                                "}"))

        widget_layout = QVBoxLayout()
        self.lbl_no_pdf = PDFLabel()
        widget_layout.addWidget(self.lbl_no_pdf, alignment=Qt.AlignCenter)
        widget.setLayout(widget_layout)

        layout.addWidget(widget)
        self.setLayout(layout)

        self.setAcceptDrops(True)

    def init_connection(self):
        self.lbl_no_pdf.double_clicked.connect(self.open_pdf)
        self.lbl_no_pdf.delete.connect(self.delete_reference)

    def delete_reference(self):
        self.delete.emit()

    def dragEnterEvent(self, event):
        if not self.contains_file:
            if event.mimeData().hasUrls():
                url = event.mimeData().urls()[0]
                suffix = QFileInfo(url.fileName()).suffix()
                if suffix == "pdf":
                    event.acceptProposedAction()

    def dropEvent(self, event):
        file = event.mimeData().urls()[0].toLocalFile()
        self.contains_file = True
        self.pdf_dropped.emit(file)

    def open_pdf(self):
        """ Open the pdf when the file is double clicked """
        if self.contains_file:
            if os.path.isfile(self.file):
                os.system("open {}".format(self.file))
            else:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Unable to locate file")
                message.setInformativeText("The reference PDF is not in the reference folder.")
                message.setIcon(QMessageBox.Information)
                message.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                message.setDefaultButton(QMessageBox.Yes)
                ret = message.exec()

                if ret == QMessageBox.Yes:
                    self.delete.emit()

    def show_pdf(self, file):
        """ Show a PDF image """
        self.file = file
        self.lbl_no_pdf.set_icon()

    def remove_pdf(self):
        """ Remove the PDF """
        self.file = None
        self.lbl_no_pdf.set_text()

    def clear_form(self):
        """ Clear all the widget element """
        self.lbl_no_pdf.set_text()
        self.contains_file = False


class PDFLabel(QLabel):
    """ Label that contains the PDF image """

    # Global variable
    contains_file = False

    # Signals
    double_clicked = pyqtSignal()
    delete = pyqtSignal()

    def __init__(self):
        super(PDFLabel, self).__init__()
        self.setWordWrap(True)
        self.set_text()
        self.setFocusPolicy(Qt.ClickFocus)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        if self.contains_file:
            self.set_icon()
        QLabel().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            self.delete.emit()
        QLabel().keyPressEvent(event)

    def focusInEvent(self, event):
        if self.contains_file:
            self.set_selected_icon()
        QLabel().focusInEvent(event)

    def focusOutEvent(self, event):
        if self.contains_file:
            self.set_icon()
        QLabel().focusOutEvent(event)

    def set_text(self):
        """ Set default text """
        self.clear()
        self.contains_file = False
        self.setText("Drop PDF here")
        self.setStyleSheet("color: rgb(172, 172, 172)")
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)

    def set_icon(self):
        """ Set PDF icon """
        image = QPixmap(":/Icons/Library/icons/library/1xpdf.png")
        if self.devicePixelRatio() == 2:
            image = QPixmap(":/Icons/Library/icons/library/2xpdf.png")
            image.setDevicePixelRatio(self.devicePixelRatio())

        self.contains_file = True
        self.setText("")
        self.setFixedSize(64, 64)
        self.setPixmap(image)

    def set_selected_icon(self):
        """ Set PDF icon """
        image = QPixmap(":/Icons/Library/icons/library/1xpdf.png")
        if self.devicePixelRatio() == 2:
            image = QPixmap(":/Icons/Library/icons/library/2xpdf.png")
            image.setDevicePixelRatio(self.devicePixelRatio())

        rect = QPainter(image)
        rect.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        pen = QPen()
        pen.setColor(QColor(140, 140, 140))
        pen.setWidth(1)
        pen.setStyle(Qt.SolidLine)
        brush = QBrush()
        brush.setColor(QColor(140, 140, 140))
        brush.setStyle(Qt.SolidPattern)
        rect.setBrush(brush)
        rect.setPen(pen)
        rect.drawRoundedRect(2, 2, 60, 60, 5, 5)
        rect.end()

        rect = QPainter(image)
        rect.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(1)
        pen.setStyle(Qt.SolidLine)
        brush = QBrush()
        brush.setColor(Qt.white)
        brush.setStyle(Qt.SolidPattern)
        rect.setBrush(brush)
        rect.setPen(pen)
        rect.drawRoundedRect(0, 0, 64, 64, 5, 5)
        rect.end()

        self.contains_file = True
        self.setText("")
        self.setFixedSize(64, 64)
        self.setPixmap(image)
