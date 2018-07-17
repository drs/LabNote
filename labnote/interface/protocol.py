""" This module contains the protocol dialog classes """

# Python import
import sqlite3
import uuid

# PyQt import
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QSettings, Qt, QItemSelectionModel, pyqtSignal

# Project import
from labnote.ui.ui_protocol import Ui_Protocol
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.interface.widget.widget import CategoryFrame, ProtocolTextEditor, NoEntryWidget
from labnote.core import stylesheet, common, data, sqlite_error
from labnote.utils import database, layout, fsentry, date
from labnote.interface.library import Library


class Protocol(QDialog, Ui_Protocol):
    """ Class responsible of managing the protocol window interface """

    # Class variable definition
    creating_protocol = False

    # Signals
    closed = pyqtSignal()

    def __init__(self, tag_list, reference_list, parent=None, prt_uuid=None):
        super(Protocol, self).__init__(parent=parent)
        # Initialize global variable
        self.tag_list = tag_list
        self.reference_list = reference_list

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()
        self.category_frame.show_list()

        if prt_uuid:
            self.show_protocol(prt_uuid)

        self.show()

    def init_ui(self):
        # General properties
        self.setWindowTitle("LabNote - Protocol")

        # Show category frame
        self.category_frame = CategoryFrame('Protocol', common.TYPE_PROTOCOL)
        self.frame.layout().insertWidget(0, self.category_frame)
        self.frame.layout().setStretch(1, 10)

        # Show search button
        self.txt_search = SearchLineEdit()
        self.layout_search.insertWidget(2, self.txt_search)

        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/protocol.qss")

        # Read settings
        self.read_settings()

    def init_connection(self):
        self.btn_close.clicked.connect(self.close)
        self.category_frame.view_tree.expanded.connect(self.save_treeview_state)
        self.category_frame.view_tree.collapsed.connect(self.save_treeview_state)
        self.category_frame.list_displayed.connect(self.restore_treeview_state)
        self.category_frame.entry_selected.connect(self.show_protocol_details)
        self.category_frame.btn_add.clicked.connect(self.start_creating_protocol)
        self.category_frame.view_tree.clicked.connect(self.clear_form)
        self.category_frame.delete.connect(self.delete_protocol)
        self.category_frame.view_tree.drop_finished.connect(self.drop_finished)

    def show_protocol(self, prt_uuid):
        """ Show the protocol with the given uuid

        :param prt_uuid: Protocol uuid
        :type prt_uuid: str
        """
        model = self.category_frame.view_tree.model()
        match = model.match(model.index(0, 0), Qt.UserRole, prt_uuid, 1, Qt.MatchRecursive)
        if match:
            self.category_frame.view_tree.selectionModel().setCurrentIndex(match[0],
                                                                           QItemSelectionModel.ClearAndSelect)
            self.category_frame.view_tree.repaint()

    def drop_finished(self, index):
        """ Update an item information after a drag and drop mouvement """
        category = self.category_frame.get_category(index)
        subcategory = self.category_frame.get_subcategory(index)

        try:
            database.update_protocol_category(self.category_frame.view_tree.selectedIndexes()[0].data(Qt.UserRole),
                                               category, subcategory)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while saving data",
                                  "An error occurred while updating the protocol category.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.category_frame.show_list()

    def show_reference(self, ref_key):
        try:
            ref_uuid = database.select_reference_uuid_key(ref_key)
        except sqlite3.Error:
            pass

        if ref_uuid:
            Library(self.tag_list, ref_uuid=data.uuid_string(ref_uuid), parent=self)

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

    def clear_form(self):
        """ Clear all data in the form """
        self.creating_protocol = False
        layout.empty_layout(self, self.layout_entry)

        index = self.category_frame.view_tree.selectionModel().currentIndex()
        if not self.category_frame.is_entry(index):
            self.layout_entry.addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)

    def delete_protocol(self, prt_uuid):
        """ Delete a protocol """
        try:
            fsentry.delete_protocol(prt_uuid=prt_uuid)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to delete protocol",
                                  "An error occurred while deleting the protocol.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return
        self.category_frame.show_list()
        self.clear_form()

    def start_creating_protocol(self):
        """ Enable new reference creation """
        if self.category_frame.get_current_level() == common.LEVEL_CATEGORY or \
                self.category_frame.get_current_level() == common.LEVEL_SUBCATEGORY or \
                self.category_frame.get_current_level() == common.LEVEL_ENTRY:
            self.creating_protocol = True
            self.create_editor()
            self.editor.btn_save.setText("Create")

    def create_editor(self, prt_uuid=None):
        """ Add the editor widget to the layout """
        layout.empty_layout(self, self.layout_entry)
        self.editor = ProtocolTextEditor(editor_type=common.TYPE_PROTOCOL, tag_list=self.tag_list,
                                         reference_list=self.reference_list)
        if prt_uuid:
            self.editor.txt_body.set_uuid(prt_uuid)
        self.editor.btn_save.clicked.connect(self.process_protocol)
        self.editor.txt_body.reference_pressed.connect(self.show_reference)
        self.layout_entry.addWidget(self.editor)

    def process_protocol(self):
        """ Process the protocol in the database and the file system """

        key = self.editor.txt_key.text()

        if key:
            # Get the current item data
            index = self.category_frame.view_tree.selectionModel().currentIndex()
            category_id = self.category_frame.get_category(index)
            subcategory_id = self.category_frame.get_subcategory(index)

            if category_id:
                # Get the protocol content
                name = data.prepare_string(self.editor.txt_title.toPlainText())
                description = data.prepare_textedit(self.editor.txt_description)
                body = self.editor.txt_body.toHtml()

                description_anchor = self.editor.txt_description.anchors()
                body_anchor = self.editor.txt_body.anchors()

                if self.creating_protocol:
                    prt_uuid = str(uuid.uuid4())

                    try:
                        fsentry.create_protocol(prt_uuid=prt_uuid, prt_key=key, category_id=category_id,
                                                name=name, subcategory_id=subcategory_id, body=body,
                                                tag_list=description_anchor['tag'],
                                                reference_list=body_anchor['reference'])
                    except (sqlite3.Error, OSError) as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create protocol")
                            message.setInformativeText("The protocol key must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create protocol")
                            message.setInformativeText("The protocol key must be unique.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to create protocol",
                                                  "An error occurred while creating the protocol.", QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return
                    self.done_modifing_protocol(prt_uuid=prt_uuid)
                else:
                    prt_uuid = self.category_frame.get_user_data()

                    try:
                        fsentry.save_protocol(prt_uuid=prt_uuid, prt_key=key, name=name, description=description,
                                              body=body, tag_list=description_anchor['tag'],
                                              reference_list=body_anchor['reference'],
                                              deleted_image=self.editor.txt_body.deleted_image)
                    except (sqlite3.Error, OSError) as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to save protocol")
                            message.setInformativeText("The protocol key must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to save protocol")
                            message.setInformativeText("The protocol key must be unique.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to save protocol",
                                                  "An error occurred while saving the protocol.", QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return
                    self.done_modifing_protocol(prt_uuid=prt_uuid)

    def done_modifing_protocol(self, prt_uuid):
        """ Active the interface element after the protocol is saved """

        # Show the protocol list
        self.category_frame.show_list()

        # End the creating protocol state
        if self.creating_protocol:
            self.creating_protocol = False
            self.editor.txt_body.set_uuid(prt_uuid)

        # Reselect the current item in the treeview
        model = self.category_frame.view_tree.model()
        match = model.match(model.index(0, 0), Qt.UserRole, prt_uuid, 1, Qt.MatchRecursive)
        if match:
            self.category_frame.view_tree.selectionModel().setCurrentIndex(match[0],
                                                                           QItemSelectionModel.ClearAndSelect)
            self.category_frame.view_tree.repaint()

        # Reset the deleted images value
        self.editor.txt_body.deleted_image = set([])

        # Update the tag list
        self.get_tag_list()

    def show_protocol_details(self, prt_uuid):
        """ Show a reference details when it is selected """
        try:
            protocol = fsentry.read_protocol(prt_uuid)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the protocol data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        # Show content
        self.create_editor(prt_uuid)
        self.editor.txt_key.setText(protocol['key'])

        name = protocol['name']
        if name:
            self.editor.txt_title.setPlainText(name)

        description = protocol['description']
        if description:
            self.editor.txt_description.setHtml(description)

        created_date = protocol['created']
        if created_date:
            self.editor.lbl_created.setText(date.utc_to_local(created_date))

        updated_date = protocol['updated']
        if updated_date:
            self.editor.lbl_updated.setText(date.utc_to_local(updated_date))

        body = protocol['body']
        if body:
            self.editor.txt_body.setHtml(body)

    def closeEvent(self, event):
        self.save_treeview_state()
        self.save_settings()
        self.closed.emit()
        event.accept()

    def save_settings(self):
        """ Save the dialog geometry """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Protocol")
        settings.setValue("Geometry", self.saveGeometry())
        settings.setValue("Maximized", self.isMaximized())
        settings.endGroup()

    def read_settings(self):
        """ Restore the dialog geometry """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Protocol")
        self.restoreGeometry(settings.value("Geometry", self.saveGeometry()))
        if settings.value("Maximized", self.isMaximized()):
            self.showMaximized()
        settings.endGroup()

    def save_treeview_state(self):
        """ Save the treeview expanded state """

        # Generate list
        expanded_item = []
        for index in self.category_frame.view_tree.model().get_persistant_index_list():
            if self.category_frame.view_tree.isExpanded(index) and index.data(common.QT_StateRole):
                expanded_item.append(index.data(common.QT_StateRole))

        # Save list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Protocol")
        settings.setValue("ExpandedItem", expanded_item)
        settings.endGroup()

    def restore_treeview_state(self):
        """ Restore the treeview expended state """

        # Get list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("Protocol")
        expanded_item = settings.value("ExpandedItem")
        selected_item = settings.value("SelectedItem")
        settings.endGroup()

        model = self.category_frame.view_tree.model()

        if expanded_item:
            for item in expanded_item:
                match = model.match(model.index(0, 0), common.QT_StateRole, item, 1, Qt.MatchRecursive)

                if match:
                    self.category_frame.view_tree.setExpanded(match[0], True)