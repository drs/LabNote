"""
This module contain the classes responsible for launching and managing the library dialog.
"""

# Python import
import sqlite3
import uuid
import os

# PyQt import
from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, QFileInfo, QItemSelectionModel
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen, QBrush

# Project import
from labnote.ui.ui_library import Ui_Library
from labnote.core import stylesheet, sqlite_error, data, common
from labnote.interface.widget.textedit import CompleterTextEdit, PlainTextEdit
from labnote.utils import database, fsentry, directory, layout
from labnote.interface.widget.lineedit import LineEdit, NumberLineEdit, YearLineEdit, SearchLineEdit
from labnote.interface.widget.widget import CategoryFrame
from labnote.interface.widget import widget
from labnote.interface.widget.object import KeyValidator


# Constant definition

# Reference type
TYPE_ARTICLE = common.TYPE_ARTICLE
TYPE_BOOK = common.TYPE_BOOK
TYPE_CHAPTER = common.TYPE_CHAPTER
TYPE_THESIS = common.TYPE_THESIS

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

    current_category = None  # Current category id
    current_subcategory = None  # Current subcategory id
    current_reference = None  # Current reference uuid

    # Signals definition
    pdf_added = pyqtSignal(str)
    pdf_deleted = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, tag_list, parent=None, ref_uuid=None):
        super(Library, self).__init__(parent)
        # Initialize global variable
        self.tag_list = tag_list

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Show the widget content
        self.category_frame.show_list()

        if ref_uuid:
            self.show_reference(ref_uuid)

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

        # Setup the form layout
        self.lbl_author = QLabel("Author")
        self.txt_author = LineEdit()
        self.layout_form.addRow(self.lbl_author, self.txt_author)

        self.lbl_title = QLabel("Title")
        self.txt_title = LineEdit()
        self.layout_form.addRow(self.lbl_title, self.txt_title)

        self.lbl_year = QLabel("Year")
        self.txt_year = YearLineEdit()
        self.layout_form.addRow(self.lbl_year, self.txt_year)

        self.lbl_chapter = QLabel("Chapter")
        self.txt_chapter = LineEdit()
        self.layout_form.addRow(self.lbl_chapter, self.txt_chapter)

        self.lbl_school = QLabel("School")
        self.txt_school = LineEdit()
        self.layout_form.addRow(self.lbl_school, self.txt_school)

        self.lbl_journal = QLabel("Journal")
        self.txt_journal = LineEdit()
        self.layout_form.addRow(self.lbl_journal, self.txt_journal)

        self.lbl_editor = QLabel("Editor")
        self.txt_editor = LineEdit()
        self.layout_form.addRow(self.lbl_editor, self.txt_editor)

        self.lbl_publisher = QLabel("Publisher")
        self.txt_publisher = LineEdit()
        self.layout_form.addRow(self.lbl_publisher, self.txt_publisher)

        self.lbl_place_published = QLabel("Place published")
        self.txt_place_published = LineEdit()
        self.layout_form.addRow(self.lbl_place_published, self.txt_place_published)

        self.lbl_volume = QLabel("Volume")
        self.txt_volume = NumberLineEdit()
        self.layout_form.addRow(self.lbl_volume, self.txt_volume)

        self.lbl_issue = QLabel("Issue")
        self.txt_issue = NumberLineEdit()
        self.layout_form.addRow(self.lbl_issue, self.txt_issue)

        self.lbl_pages = QLabel("Pages")
        self.txt_pages = LineEdit()
        self.layout_form.addRow(self.lbl_pages, self.txt_pages)

        self.lbl_edition = QLabel("Edition")
        self.txt_edition = LineEdit()
        self.layout_form.addRow(self.lbl_edition, self.txt_edition)

        self.lbl_description = QLabel("Description")
        self.txt_description = CompleterTextEdit(self.tag_list)
        self.layout_form.addRow(self.lbl_description, self.txt_description)

        self.lbl_abstract = QLabel("Abstract")
        self.txt_abstract = PlainTextEdit()
        self.layout_form.addRow(self.lbl_abstract, self.txt_abstract)

        self.layout_form.setLabelAlignment(Qt.AlignLeft)
        self.main_frame.setStyleSheet(" QLineEdit { margin-bottom: 4px; } "
                                      " QTextEdit { margin-bottom: 4px; }")

        self.txt_key.setStyleSheet("QLineEdit { margin-bottom: 0px;}")

        self.enable_all(False)
        self.article_field()

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/library.qss")

        # Remove focus rectangle
        self.txt_key.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Key size
        self.lbl_key.setFixedSize(102, 21)

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
        self.category_frame.view_tree.clicked.connect(self.selection_change)

        self.txt_key.textChanged.connect(self.set_window_modified)
        self.txt_author.textChanged.connect(self.set_window_modified)
        self.txt_title.textChanged.connect(self.set_window_modified)
        self.txt_year.textChanged.connect(self.set_window_modified)
        self.txt_chapter.textChanged.connect(self.set_window_modified)
        self.txt_school.textChanged.connect(self.set_window_modified)
        self.txt_journal.textChanged.connect(self.set_window_modified)
        self.txt_editor.textChanged.connect(self.set_window_modified)
        self.txt_publisher.textChanged.connect(self.set_window_modified)
        self.txt_place_published.textChanged.connect(self.set_window_modified)
        self.txt_volume.textChanged.connect(self.set_window_modified)
        self.txt_issue.textChanged.connect(self.set_window_modified)
        self.txt_pages.textChanged.connect(self.set_window_modified)
        self.txt_edition.textChanged.connect(self.set_window_modified)
        self.txt_description.textChanged.connect(self.set_window_modified)
        self.txt_abstract.textChanged.connect(self.set_window_modified)

    def selection_change(self, index):
        """ Set the current category, subcategory and reference value """
        self.creating_reference = False
        self.current_category = self.category_frame.get_category(index)
        self.current_subcategory = self.category_frame.get_subcategory(index)

        self.clear_form()
        self.setWindowModified(False)
        self.enable_all(False)

        if self.category_frame.is_entry(index):
            self.current_reference = index.data(Qt.UserRole)
            self.show_reference_details()
        else:
            self.current_reference = None

    def show_reference(self, ref_uuid):
        """ Show the reference with the given uuid

        :param ref_uuid: Reference uuid
        :type ref_uuid: str
        """
        model = self.category_frame.view_tree.model()
        match = model.match(model.index(0, 0), Qt.UserRole, ref_uuid, 1, Qt.MatchRecursive)
        if match:
            self.category_frame.view_tree.selectionModel().setCurrentIndex(match[0],
                                                                           QItemSelectionModel.ClearAndSelect)
            self.selection_change(match[0])
            self.category_frame.view_tree.repaint()

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

        self.current_category = category
        self.current_subcategory = subcategory

        self.category_frame.show_list()
        self.done_modifing_reference(self.current_reference)

    def show_reference_details(self):
        """ Show a reference details when it is selected """

        try:
            reference = database.select_reference(self.current_reference)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the reference data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.enable_all(True)

        # Set text
        self.txt_key.setText(data.receive_string(reference['key']))
        self.txt_author.setText(data.receive_string(reference['author']))
        self.txt_title.setText(data.receive_string(reference['title']))
        self.txt_year.setText(data.receive_string(reference['year']))
        self.txt_chapter.setText(data.receive_string(reference['chapter']))
        self.txt_school.setText(data.receive_string(reference['school']))
        self.txt_journal.setText(data.receive_string(reference['journal']))
        self.txt_editor.setText(data.receive_string(reference['editor']))
        self.txt_publisher.setText(data.receive_string(reference['publisher']))
        self.txt_place_published.setText(data.receive_string(reference['place']))
        self.txt_volume.setText(data.receive_string(reference['volume']))
        self.txt_issue.setText(data.receive_string(reference['issue']))
        self.txt_pages.setText(data.receive_string(reference['pages']))
        self.txt_edition.setText(data.receive_string(reference['edition']))
        self.txt_description.setHtml(data.receive_string(reference['description']))
        self.txt_abstract.setPlainText(data.receive_string(reference['abstract']))

        # Set current item in the combobox
        if reference['type'] == TYPE_ARTICLE:
            self.comboBox.setCurrentText('Article')
        elif reference['type'] == TYPE_BOOK:
            self.comboBox.setCurrentText('Book')
        elif reference['type'] == TYPE_CHAPTER:
            self.comboBox.setCurrentText('Chapter')
        elif reference['type'] == TYPE_THESIS:
            self.comboBox.setCurrentText('Thesis')

        # Show the PDF file
        if reference['file']:
            file = os.path.join(directory.REFERENCES_DIRECTORY_PATH + "/{}.pdf".format(reference['uuid']))
            self.pdf_widget.show_pdf(file=file)

        self.setWindowModified(False)

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
        self.txt_key.clear()
        self.comboBox.setCurrentText("Article")
        for position in range(0, self.layout_form.count()-1):
            item = self.layout_form.itemAt(position)
            widget = item.widget()
            if type(widget) == LineEdit or type(widget) == NumberLineEdit or type(widget) == YearLineEdit:                widget.clear()
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

    def set_window_modified(self):
        self.setWindowModified(True)

    def enable_all(self, enable):
        """ Disable all items in the layout

        :param enable: Enable state
        :type enable: bool
        """
        self.btn_save.setEnabled(enable)
        layout.disable_layout(self.layout_form, enable)
        self.pdf_widget.setEnabled(enable)

    def process_reference(self):
        """ Create the reference in the database """

        key = self.txt_key.text()

        if key:
            if self.current_category:
                ref_type = self.comboBox.currentText()
                anchor = self.txt_description.anchors()

                author = data.prepare_string(self.txt_author.text())
                title = data.prepare_string(self.txt_title.text())
                year = data.prepare_string_number(self.txt_year.text())
                chapter = data.prepare_string(self.txt_chapter.text())
                school = data.prepare_string(self.txt_school.text())
                journal = data.prepare_string(self.txt_journal.text())
                editor = data.prepare_string(self.txt_editor.text())
                publisher = data.prepare_string(self.txt_publisher.text())
                place = data.prepare_string(self.txt_place_published.text())
                volume = data.prepare_string_number(self.txt_volume.text())
                issue = data.prepare_string_number(self.txt_issue.text())
                pages = data.prepare_string(self.txt_pages.text())
                edition = data.prepare_string_number(self.txt_edition.text())
                description = data.prepare_textedit(self.txt_description)
                abstract = data.prepare_string(self.txt_abstract.toPlainText())

                if self.creating_reference:
                    ref_uuid = data.uuid_bytes(uuid.uuid4())
                    try:
                        if ref_type == "Article":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, ref_type=TYPE_ARTICLE,
                                                category_id=self.current_category,
                                                subcategory_id=self.current_subcategory, author=author,
                                                title=title, journal=journal, year=year, volume=volume, issue=issue,
                                                pages=pages, description=description, abstract=abstract,
                                                tag_list=anchor['tag'])
                        elif ref_type == "Book":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=self.current_category,
                                                subcategory_id=self.current_subcategory,
                                                author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                ref_type=TYPE_BOOK, tag_list=anchor['tag'])
                        elif ref_type == "Chapter":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=self.current_category,
                                                subcategory_id=self.current_subcategory,
                                                author=author, title=title, year=year,
                                                publisher=publisher, address=place, volume=volume, pages=pages,
                                                edition=edition, description=description, abstract=abstract,
                                                chapter=chapter, editor=editor, ref_type=TYPE_CHAPTER,
                                                tag_list=anchor['tag'])
                        elif ref_type == "Thesis":
                            database.insert_ref(ref_uuid=ref_uuid, ref_key=key, category_id=self.current_category,
                                                subcategory_id=self.current_subcategory,
                                                author=author, title=title, year=year,
                                                address=place, description=description,
                                                abstract=abstract, school=school,
                                                ref_type=TYPE_THESIS, tag_list=anchor['tag'])
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
                    if self.current_reference:
                        ref_uuid = data.uuid_bytes(self.current_reference)
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
                            elif ref_type == "Thesis":
                                database.update_ref(ref_uuid=ref_uuid, ref_key=key, author=author, title=title, year=year,
                                                    address=place, description=description, abstract=abstract,
                                                    school=school, ref_type=TYPE_THESIS, tag_list=anchor['tag'])

                            self.done_modifing_reference(ref_uuid=data.uuid_string(ref_uuid))
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
            self.category_frame.view_tree.selectionModel().setCurrentIndex(match[0],
                                                                           QItemSelectionModel.ClearAndSelect)
            self.category_frame.view_tree.repaint()
        self.get_tag_list()

    def show_field(self, text):
        """ Show the field related to a specific type of literature """

        # Show appropriate fields
        if text == "Article":
            self.article_field()
        elif text == "Book":
            self.book_field()
        elif text == "Chapter":
            self.chapter_field()
        elif text == "Thesis":
            self.thesis_field()

    def set_visible(self, visible):
        """ Set the interface visible value

        :param visible:
        :type {}: Name and bool visible value
        """

        for key, value in visible.items():
            if key == 'author':
                self.set_field_visible(self.lbl_author, self.txt_author, value)
            elif key == 'title':
                self.set_field_visible(self.lbl_title, self.txt_title, value)
            elif key == 'year':
                self.set_field_visible(self.lbl_year, self.txt_year, value)
            elif key == 'chapter':
                self.set_field_visible(self.lbl_chapter, self.txt_chapter, value)
            elif key == 'school':
                self.set_field_visible(self.lbl_school, self.txt_school, value)
            elif key == 'journal':
                self.set_field_visible(self.lbl_journal, self.txt_journal, value)
            elif key == 'editor':
                self.set_field_visible(self.lbl_editor, self.txt_editor, value)
            elif key == 'publisher':
                self.set_field_visible(self.lbl_publisher, self.txt_publisher, value)
            elif key == 'place':
                self.set_field_visible(self.lbl_place_published, self.txt_place_published, value)
            elif key == 'volume':
                self.set_field_visible(self.lbl_volume, self.txt_volume, value)
            elif key == 'issue':
                self.set_field_visible(self.lbl_issue, self.txt_issue, value)
            elif key == 'pages':
                self.set_field_visible(self.lbl_pages, self.txt_pages, value)
            elif key == 'edition':
                self.set_field_visible(self.lbl_edition, self.txt_edition, value)
            elif key == 'description':
                self.set_field_visible(self.lbl_description, self.txt_description, value)
            elif key == 'abstract':
                self.set_field_visible(self.lbl_abstract, self.txt_abstract, value)

    def set_field_visible(self, label, txt, visible):
        """ Set a specific field visible

        :param label: Field label
        :type label: QLabel
        :param txt: Field lineedit
        :type txt: QLineEdit or QTextEdit subclass
        :param visible: Visible or not value
        :type visible: bool
        """
        if visible:
            label.setVisible(True)
            txt.setVisible(True)
        else:
            label.setVisible(False)
            txt.setVisible(False)
            txt.clear()

    def article_field(self):
        """ Show all the article related fields in the layout """

        visible = {'author': True,
                   'title': True,
                   'year': True,
                   'chapter': False,
                   'school': False,
                   'journal': True,
                   'editor': False,
                   'publisher': False,
                   'place': False,
                   'volume': True,
                   'issue': True,
                   'pages': True,
                   'edition': False,
                   'description': True,
                   'abstract': True}
        self.set_visible(visible)

    def book_field(self):
        """ Show all the book related fields in the layout """

        visible = {'author': True,
                   'title': True,
                   'year': True,
                   'chapter': False,
                   'school': False,
                   'journal': False,
                   'editor': False,
                   'publisher': True,
                   'place': True,
                   'volume': True,
                   'issue': False,
                   'pages': True,
                   'edition': True,
                   'description': True,
                   'abstract': True}
        self.set_visible(visible)

    def chapter_field(self):
        """ Show all the chapter related fields in the layout """

        visible = {'author': True,
                   'title': True,
                   'year': True,
                   'chapter': True,
                   'school': False,
                   'journal': False,
                   'editor': True,
                   'publisher': True,
                   'place': True,
                   'volume': True,
                   'issue': False,
                   'pages': True,
                   'edition': True,
                   'description': True,
                   'abstract': True}
        self.set_visible(visible)

    def thesis_field(self):
        """ Show all the chapter related fields in the layout """

        visible = {'author': True,
                   'title': True,
                   'year': True,
                   'chapter': False,
                   'school': True,
                   'journal': False,
                   'editor': False,
                   'publisher': False,
                   'place': True,
                   'volume': False,
                   'issue': False,
                   'pages': False,
                   'edition': False,
                   'description': True,
                   'abstract': True}
        self.set_visible(visible)

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
        self.contains_file = True
        self.file = file
        self.lbl_no_pdf.set_icon()

    def remove_pdf(self):
        """ Remove the PDF """
        self.contains_file = False
        self.file = None
        self.lbl_no_pdf.set_text()

    def clear_form(self):
        """ Clear all the widget element """
        self.contains_file = False
        self.lbl_no_pdf.set_text()


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
