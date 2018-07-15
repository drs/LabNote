"""
This module contain the classes responsible for launching and managing the LabNote MainWindow.
"""

# Python import
import sqlite3
import uuid

# PyQt import
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QAction, QSizePolicy, QMenu, QLabel, QVBoxLayout, \
    QListWidgetItem
from PyQt5.QtGui import QIcon, QFont, QStandardItem
from PyQt5.QtCore import Qt, QSettings, QByteArray, pyqtSignal, QItemSelectionModel

# Project import
from labnote.ui.ui_mainwindow import Ui_MainWindow
from labnote.core import stylesheet, common, data, sqlite_error
from labnote.utils import database, fsentry, layout, date
from labnote.interface import project, library, sample, dataset, protocol
from labnote.interface.dialog.notebook import Notebook
from labnote.interface.widget.lineedit import TagSearchLineEdit
from labnote.interface.widget.view import TreeView
from labnote.interface.widget.model import StandardItemModel
from labnote.interface.widget.widget import NoEntryWidget, ExperimentTextEditor


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class responsible of launching the LabNote MainWindow interface.
    """
    
    # Class variable definition
    tag_list = []
    reference_list = []
    dataset_list = []
    protocol_list = []
    creating_experiment = False
    current_experiment = None
    current_notebook = None

    def __init__(self):
        super(MainWindow, self).__init__()
        # Check files integrity
        self.check_main_directory()

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Read program settings
        self.read_settings()

    def init_ui(self):
        """ Initialize all the GUI elements """

        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/main_window.qss")

        # Set window title
        self.setWindowTitle("LabNote")

        # Unified toolbar on mac
        self.setUnifiedTitleAndToolBarOnMac(True)

        # Set toolbar icons
        self.act_new.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/new-experiment.png"))
        self.act_duplicate.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/duplicate.png"))
        self.act_share.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/share.png"))
        self.act_dataset.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/dataset.png"))
        self.act_protocols.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/protocols.png"))
        self.act_project.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/project.png"))
        self.act_library.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/library.png"))
        self.act_samples.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/sample.png"))

        # Get list
        self.get_tag_list()
        self.get_reference_list()
        self.get_dataset_list()
        self.get_protocol_list()

        # Set toolbar separator
        empty_widget_1 = QWidget()
        empty_widget_1.setFixedWidth(130)
        self.experiment_toolbar.insertWidget(self.act_new, empty_widget_1)

        empty_widget_2 = QWidget()
        empty_widget_2.setFixedWidth(90)
        self.data_toolbar.insertWidget(self.act_protocols, empty_widget_2)

        empty_widget_3 = QWidget()
        empty_widget_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.search_toolbar.addWidget(empty_widget_3)

        self.txt_search = TagSearchLineEdit(self.tag_list)
        self.search_toolbar.addWidget(self.txt_search)

        empty_widget_4 = QWidget()
        empty_widget_4.setFixedWidth(10)
        self.search_toolbar.addWidget(empty_widget_4)

        # Set notebook settings button menu
        self.notebook_setting_menu = QMenu(self)
        self.notebook_setting_menu.setFont(QFont(self.font().family(), 13, QFont.Normal))
        self.act_delete_notebook = QAction("Delete notebook", self)
        self.act_delete_notebook.triggered.connect(self.delete_notebook)
        self.act_delete_notebook.setEnabled(False)
        self.notebook_setting_menu.addAction(self.act_delete_notebook)
        self.act_rename_notebook = QAction("Update notebook", self)
        self.act_rename_notebook.triggered.connect(self.update_notebook)
        self.act_rename_notebook.setEnabled(False)
        self.notebook_setting_menu.addAction(self.act_rename_notebook)
        self.btn_settings.setMenu(self.notebook_setting_menu)

        # Disable the notebook and experiment related actions from toolbar
        self.act_new.setEnabled(False)
        self.act_share.setEnabled(False)
        self.act_duplicate.setEnabled(False)

        # Remove focus rectangle
        self.lst_entry.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Create the notebook list widget
        self.view_notebook = ProjectNotebookTreeView()
        self.frame.layout().insertWidget(1, self.view_notebook)

        # Add no entry widget widget to mainwindow
        self.layout_experiment.addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)

    def init_connection(self):
        self.btn_add_notebook.clicked.connect(self.create_notebook)
        self.view_notebook.selection_changed.connect(self.notebook_selection_change)
        self.act_save.triggered.connect(self.process_experiment)
        #self.act_new.triggered.connect(self.create_experiment)
        #self.act_new_experiment.triggered.connect(self.create_experiment)
        self.act_project.triggered.connect(self.open_project)
        self.act_library.triggered.connect(self.open_library)
        self.act_samples.triggered.connect(self.open_sample)
        self.act_dataset.triggered.connect(self.open_dataset)
        self.act_protocols.triggered.connect(self.open_protocol)
        self.act_mb_protocol.triggered.connect(self.open_protocol)
        self.act_mb_dataset.triggered.connect(self.open_dataset)
        self.act_mb_library.triggered.connect(self.open_library)
        self.act_mb_sample.triggered.connect(self.open_sample)
        self.act_new.triggered.connect(self.start_creating_experiment)
        self.act_mb_new.triggered.connect(self.start_creating_experiment)
        self.lst_entry.itemSelectionChanged.connect(self.experiment_selection_change)

    """
    General functions
    """

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

    def get_reference_list(self):
        """ Get the list of all tag """
        reference_list = []

        try:
            reference_list = database.select_reference_key()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to get reference list",
                                  "An error occurred while getting the reference list.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.reference_list = reference_list

    def get_protocol_list(self):
        """ Get the list of all tag """
        protocol_list = []

        try:
            protocol_list = database.select_protocol_key()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to get tag list",
                                  "An error occurred while getting the tag list.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.protocol_list = protocol_list

    def get_dataset_list(self):
        """ Get the list of all tag """
        dataset_list = []

        try:
            dataset_list = database.select_dataset_key()
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Unable to get tag list",
                                  "An error occurred while getting the tag list.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        self.dataset_list = dataset_list

    def closeEvent(self, e):
        """
        Write the program geometry and state to settings
        :param e: Close event
        :type e: QCloseEvent
        :returns: Event for the parent
        """
        # Write the settings
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.setValue("MainWindow/Geometry", self.saveGeometry())

        return super(MainWindow, self).closeEvent(e)

    def read_settings(self):
        """ Read the setting when program launch to restore geometry and state """

        settings = QSettings("Samuel Drouin", "LabNote")
        self.restoreGeometry(settings.value("MainWindow/Geometry", QByteArray()))

    def check_main_directory(self):
        """ Check if the main directory and database exist """
        try:
            fsentry.check_main_directory()
        except (sqlite3.Error, OSError) as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unexpected error occured")
            message.setInformativeText("An unexpected error occurred while checking the main directory integrity "
                                       "The program operation might be affected.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    """
    Toolbar and menu bar functions
    """

    def open_project(self):
        """ Open the project dialog """
        proj = project.Project(self)
        proj.closed.connect(self.view_notebook.show_content)

    def open_library(self):
        """ Open the library dialog """
        lib = library.Library(tag_list=self.tag_list, parent=self)
        lib.closed.connect(self.get_tag_list)
        lib.closed.connect(self.get_reference_list)

    def open_sample(self):
        """ Open the sample number dialog """
        sample.Sample(self)

    def open_dataset(self):
        """ Open the dataset dialog """
        dt = dataset.Dataset(self)
        dt.closed.connect(self.get_dataset_list)

    def open_protocol(self):
        """ Open the protocol dialog """
        prt = protocol.Protocol(tag_list=self.tag_list, reference_list=self.reference_list, parent=self)
        prt.closed.connect(self.get_tag_list)
        prt.closed.connect(self.get_protocol_list)

    """
    Notebook list functions
    """

    def create_notebook(self):
        """ Show a sheet dialog that create a new notebook. """
        self.notebook = Notebook()
        self.notebook.setWindowModality(Qt.WindowModal)
        self.notebook.setParent(self, Qt.Sheet)
        self.notebook.show()
        self.notebook.accepted.connect(self.view_notebook.show_content)

    def notebook_selection_change(self, hierarchy_level, item_id):
        """ This function is called when the notebook or project change

        It activate the buttons depending on the active item or show the experiment.
        """

        self.creating_experiment = False
        self.current_notebook = None
        self.current_experiment = None
        self.clear_form()
        self.lst_entry.blockSignals(True)
        self.lst_entry.clear()
        self.lst_entry.blockSignals(False)

        if hierarchy_level == 1:
            self.act_delete_notebook.setEnabled(False)
            self.act_rename_notebook.setEnabled(False)
            self.act_new.setEnabled(False)
            self.current_notebook = None
        elif hierarchy_level == 2:
            self.act_delete_notebook.setEnabled(True)
            self.act_rename_notebook.setEnabled(True)
            self.act_new.setEnabled(True)
            self.current_notebook = item_id
            self.show_experiment_list()

    def delete_notebook(self):
        """ Delete a notebook """

        # Get the notebook informations
        current_data = self.view_notebook.current_selection()
        nb_uuid = current_data[0]
        nb_name = current_data[1]

        # Confirm if the user really want to delete the notebook
        confirmation_messagebox = QMessageBox()
        confirmation_messagebox.setWindowTitle("LabNote")
        confirmation_messagebox.setText("Delete notebook")
        confirmation_messagebox.setInformativeText("Do you want to delete the notebook '{}'".format(nb_name))
        confirmation_messagebox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        confirmation_messagebox.setDefaultButton(QMessageBox.Cancel)
        confirmation_messagebox.setIcon(QMessageBox.Question)
        confirmation_message = confirmation_messagebox.exec()

        # Delete the notebook from the database
        if confirmation_message == QMessageBox.Ok:
            try:
                fsentry.delete_notebook(nb_uuid=nb_uuid)
            except (sqlite3.Error, OSError) as exception:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Cannot delete notebook")
                message.setInformativeText("An error occurred while deleting the notebook")
                message.setDetailedText(str(exception))
                message.setIcon(QMessageBox.Warning)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()

        self.view_notebook.show_content()

    def update_notebook(self):
        """ Show a dialog to update a category """

        # Get the category informations
        index = self.view_notebook.selectionModel().currentIndex()

        name = index.data(Qt.DisplayRole)
        notebook_id = index.data(Qt.UserRole)
        project_id = self.view_notebook.get_project(index)

        # Show the dialog
        notebook = Notebook(name=name, notebook_id=notebook_id, project_id=project_id)
        notebook.lbl_title.setText("Update a notebook")
        notebook.setWindowModality(Qt.WindowModal)
        notebook.setParent(self, Qt.Sheet)
        notebook.show()
        notebook.accepted.connect(self.view_notebook.show_content)

    """
    Experiment functions
    """

    def start_creating_experiment(self):
        """ Enable new reference creation """
        if self.view_notebook.get_current_level() == common.LEVEL_NOTEBOOK:
            self.creating_experiment = True
            self.create_editor()

    def create_editor(self):
        """ Add the editor widget to the layout """
        layout.empty_layout(self, self.layout_experiment)

        try:
            key_list = database.select_experiment_key_notebook(self.view_notebook.get_user_data())
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unable to select expriment key")
            message.setInformativeText("An unhandeled error occured while selecting the experiment key for the current "
                                       "notebook.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
            return

        self.editor = ExperimentTextEditor(tag_list=self.tag_list, reference_list=self.reference_list,
                                           dataset_list=self.dataset_list, protocol_list=self.protocol_list,
                                           key_list=key_list)
        if self.current_experiment:
            self.editor.txt_body.set_uuid(uuid=self.current_experiment, parent_uuid=self.current_notebook)
        self.editor.txt_body.reference_pressed.connect(self.show_reference)
        self.editor.txt_body.dataset_pressed.connect(self.show_dataset)
        self.editor.txt_body.protocol_pressed.connect(self.show_protocol)
        self.layout_experiment.addWidget(self.editor)

    def show_reference(self, ref_key):
        try:
            ref_uuid = database.select_reference_uuid_key(ref_key)
        except sqlite3.Error:
            return

        if ref_uuid:
            library.Library(self.tag_list, ref_uuid=data.uuid_string(ref_uuid), parent=self)

    def show_dataset(self, dt_key):
        try:
            dt_uuid = database.select_dataset_uuid_key(dt_key)
        except sqlite3.Error:
            return

        if dt_uuid:
            dataset.Dataset(self.tag_list, dt_uuid=data.uuid_string(dt_uuid), parent=self)

    def show_protocol(self, prt_key):
        try:
            prt_uuid = database.select_protocol_uuid_key(prt_key)
        except sqlite3.Error:
            return

        if prt_uuid:
            protocol.Protocol(self.tag_list, dt_uuid=data.uuid_string(prt_uuid), parent=self)

    def process_experiment(self):
        """ Process the experiment in the database and the file system """

        if self.current_experiment is not None or self.creating_experiment:
            nb_uuid = self.view_notebook.get_user_data()
            name = data.prepare_string(self.editor.txt_title.toPlainText())

            if nb_uuid and name:
                # Get the experiment content
                key = data.prepare_string(self.editor.txt_key.text())
                description = data.prepare_textedit(self.editor.txt_description)
                body = self.editor.txt_body.toHtml()

                description_anchor = self.editor.txt_description.anchors()
                body_anchor = self.editor.txt_body.anchors()

                if self.creating_experiment:
                    exp_uuid = str(uuid.uuid4())

                    try:
                        fsentry.create_experiment(exp_uuid=exp_uuid, nb_uuid=nb_uuid, name=name, exp_key=key,
                                                  description=description, body=body, tag_list=description_anchor['tag'],
                                                  reference_list=body_anchor['reference'],
                                                  dataset_list=body_anchor['dataset'],
                                                  protocol_list=body_anchor['protocol'])
                    except (sqlite3.Error, OSError) as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create experiment")
                            message.setInformativeText("The experiment name must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to create experiment")
                            message.setInformativeText("The experiment key must be unique within a notebook.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to create experiment",
                                                  "An unhandled error occurred while creating the experiment.",
                                                  QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return
                    self.done_modifing_protocol(exp_uuid)
                else:
                    exp_uuid = self.current_experiment

                    try:
                        fsentry.save_experiment(exp_uuid=exp_uuid, nb_uuid=nb_uuid, name=name, exp_key=key,
                                                description=description, body=body,
                                                tag_list=description_anchor['tag'],
                                                reference_list=body_anchor['reference'],
                                                dataset_list=body_anchor['dataset'],
                                                protocol_list=body_anchor['protocol'],
                                                deleted_image=self.editor.txt_body.deleted_image)
                    except (sqlite3.Error, OSError) as exception:
                        error_code = sqlite_error.sqlite_err_handler(str(exception))

                        if error_code == sqlite_error.NOT_NULL_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to save experiment")
                            message.setInformativeText("The experiment name must not be empty.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        elif error_code == sqlite_error.UNIQUE_CODE:
                            message = QMessageBox()
                            message.setWindowTitle("LabNote")
                            message.setText("Unable to save experiment")
                            message.setInformativeText("The experiment key must be unique within a notebook.")
                            message.setIcon(QMessageBox.Information)
                            message.setStandardButtons(QMessageBox.Ok)
                            message.exec()
                            return
                        else:
                            message = QMessageBox(QMessageBox.Warning, "Unable to save experiment",
                                                  "An unhandled error occurred while saving the experiment.",
                                                  QMessageBox.Ok)
                            message.setWindowTitle("LabNote")
                            message.setDetailedText(str(exception))
                            message.exec()
                            return
                    self.done_modifing_protocol(exp_uuid)

    def experiment_selection_change(self):
        if self.lst_entry.currentItem().data(Qt.UserRole):
            self.current_experiment = self.lst_entry.currentItem().data(Qt.UserRole)
            self.show_experiment_details()

    def done_modifing_protocol(self, exp_uuid):
        """ Active the interface element after the protocol is saved """
        self.current_experiment = exp_uuid
        self.show_experiment_list(current_item=self.current_experiment)

        if self.creating_experiment:
            self.creating_experiment = False
            self.editor.txt_body.set_uuid(uuid=self.current_experiment, parent_uuid=self.current_notebook)

        self.get_tag_list()

    def clear_form(self):
        """ Clear all data in the form """
        layout.empty_layout(self, self.layout_experiment)

        if not self.current_experiment:
            self.layout_experiment.addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)

    def show_experiment_list(self, current_item=None):
        """ Show the list of experiment for the open notebook. """

        # Clear the existing list
        self.lst_entry.clear()

        # Get experiment list
        try:
            buffer = database.get_experiment_list_notebook(data.uuid_bytes(self.current_notebook))
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the experiment list")
            message.setInformativeText("An error occurred while getting the experiment list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()
            return

        if buffer:
            to_be_current_item = None
            for experiment in buffer:
                list_widget_item = QListWidgetItem()

                widget = ListWidget(experiment['name'], experiment['key'])
                list_widget_item.setData(Qt.UserRole, data.uuid_string(experiment['exp_uuid']))

                # Add widget to list
                list_widget_item.setSizeHint(widget.sizeHint())
                self.lst_entry.addItem(list_widget_item)
                self.lst_entry.setItemWidget(list_widget_item, widget)

                # Set the current item
                if current_item:
                    if data.uuid_string(experiment['exp_uuid']) == current_item:
                        print(current_item)
                        to_be_current_item = list_widget_item
                        print(to_be_current_item)

            if to_be_current_item:
                self.lst_entry.setCurrentItem(to_be_current_item)
            else:
                self.lst_entry.setCurrentRow(0)

    def show_experiment_details(self):
        """ Show a reference details when it is selected """
        layout.empty_layout(self, self.layout_experiment)
        try:
            protocol = fsentry.read_experiment(self.current_notebook, self.current_experiment)
        except sqlite3.Error as exception:
            message = QMessageBox(QMessageBox.Warning, "Error while loading data",
                                  "An error occurred while loading the experiment data.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()
            return

        # Show content
        self.create_editor()
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


class ProjectNotebookTreeView(TreeView):
    """ This class manage the data in the project and notebook tree widget """

    # Define global constant
    QT_LevelRole = Qt.UserRole + 1

    # Signal definition
    selection_changed = pyqtSignal(int, str)

    def __init__(self):
        super(ProjectNotebookTreeView, self).__init__()
        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/view/project_notebook_tree_view.qss")

        self.show_content()

        self.collapsed.connect(self.save_state)
        self.expanded.connect(self.save_state)
        
    def get_user_data(self):
        """ Return the data in the current item for user role """
        index = self.selectionModel().currentIndex()
        return index.data(Qt.UserRole)

    def get_current_level(self):
        """ Return the level of the current item """
        index = self.selectionModel().currentIndex()
        return index.data(self.QT_LevelRole)

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
                project_item.setData(common.LEVEL_PROJECT, self.QT_LevelRole)
                project_item.setFont(QFont(self.font().family(), 12, QFont.Bold))
                root.appendRow(project_item)

                if project.notebook:
                    for notebook in project.notebook:
                        notebook_item = QStandardItem(notebook.name)
                        notebook_item.setData(notebook.uuid, Qt.UserRole)
                        notebook_item.setData(common.LEVEL_NOTEBOOK, self.QT_LevelRole)
                        project_item.appendRow(notebook_item)

        self.setModel(model)
        self.selectionModel().setCurrentIndex(self.model().index(0, 0),
                                              QItemSelectionModel.ClearAndSelect)
        self.selectionModel().currentChanged.connect(self.selection_change)
        self.restore_state()

    def get_hierarchy_level(self, index):
        """ Get the hierarchy level for the index

        :param index: Item index
        :type index: QModelIndex
        :return int: Hierarchy level
        """
        if index.data(self.QT_LevelRole) == common.LEVEL_PROJECT:
            return 1
        elif index.data(self.QT_LevelRole) == common.LEVEL_NOTEBOOK:
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
        settings.beginGroup("MainWindow")
        settings.setValue("ExpandedItem", expanded_item)
        settings.endGroup()

    def restore_state(self):
        """ Restore the treeview expended state """

        # Get list
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.beginGroup("MainWindow")
        expanded_item = settings.value("ExpandedItem")
        selected_item = settings.value("SelectedItem")
        settings.endGroup()

        model = self.model()

        if expanded_item:
            for item in expanded_item:
                match = model.match(model.index(0, 0), Qt.UserRole, item, 1, Qt.MatchRecursive)

                if match:
                    self.setExpanded(match[0], True)


class ListWidget(QWidget):
    """ Item in the list widget """
    def __init__(self, title, key):
        super(ListWidget, self).__init__()
        lbl_key = QLabel(key)
        lbl_title = QLabel(title)
        layout = QVBoxLayout()
        layout.addWidget(lbl_key)
        layout.addWidget(lbl_title)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)
        self.setLayout(layout)
