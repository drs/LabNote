"""
This module contain the classes responsible for launching and managing the LabNote MainWindow.
"""

# Python import
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QLabel, QAction, QSizePolicy, QMenu
from PyQt5.QtGui import QPixmap, QIcon, QFont, QStandardItem
from PyQt5.QtCore import Qt, QSettings, QByteArray, pyqtSignal

# Project import
from labnote.ui.ui_mainwindow import Ui_MainWindow
from labnote.core import stylesheet
from labnote.utils import database, directory, fsentry
from labnote.interface import project, library, sample, dataset, protocol
from labnote.interface.dialog.notebook import Notebook
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.interface.widget.view import TreeView
from labnote.interface.widget.model import StandardItemModel
from labnote.interface.widget.widget import NoEntryWidget


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class responsible of launching the LabNote MainWindow interface.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        # Class variable definition
        self.current_nb_uuid = None
        self.current_exp_uuid = None
        self.current_exp_name = None
        self.name_updated = False
        self.current_exp_objective = None
        self.objective_updated = False
        self.current_exp_body = None
        self.body_updated = False

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

        self.txt_search = SearchLineEdit()
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
        self.act_new_experiment.setEnabled(False)
        self.act_share.setEnabled(False)
        self.act_duplicate.setEnabled(False)

        # Remove focus rectangle
        self.lst_entry.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Create the notebook list widget
        self.view_notebook = ProjectNotebookTreeView()
        self.frame.layout().insertWidget(1, self.view_notebook)

        # Add no entry widget widget to mainwindow
        self.centralWidget().layout().addWidget(NoEntryWidget(), Qt.AlignHCenter, Qt.AlignCenter)

    def init_connection(self):
        self.btn_add_notebook.clicked.connect(self.create_notebook)
        self.view_notebook.selection_changed.connect(self.notebook_changed)
        #self.act_new.triggered.connect(self.create_experiment)
        #self.act_new_experiment.triggered.connect(self.create_experiment)
        #self.lst_entry.itemSelectionChanged.connect(self.experiment_changed)
        self.act_project.triggered.connect(self.open_project)
        self.act_library.triggered.connect(self.open_library)
        self.act_samples.triggered.connect(self.open_sample_number)
        self.act_dataset.triggered.connect(self.open_dataset)
        self.act_protocols.triggered.connect(self.open_protocol)

    """
    General functions
    """

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
    Toolbar functions
    """

    def open_project(self):
        """ Open the project dialog """
        proj = project.Project(self)
        proj.closed.connect(self.view_notebook.show_content)

    def open_library(self):
        """ Open the library dialog """
        library.Library(self)

    def open_sample_number(self):
        """ Open the sample number dialog """
        sample.Sample(self)

    def open_dataset(self):
        """ Open the dataset dialog """
        dataset.Dataset(self)

    def open_protocol(self):
        """ Open the protocol dialog """
        protocol.Protocol(self)

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

    def notebook_changed(self, hierarchy_level, item_id):
        """ This function is called when the notebook or project change

        It activate the buttons depending on the active item or show the experiment.
        """
        if hierarchy_level == 1:
            self.act_delete_notebook.setEnabled(False)
            self.act_rename_notebook.setEnabled(False)
            self.act_new.setEnabled(False)
        elif hierarchy_level == 2:
            self.act_delete_notebook.setEnabled(True)
            self.act_rename_notebook.setEnabled(True)
            self.act_new.setEnabled(True)

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

    # """
    # Experiment list functions
    # """
    # def create_experiment(self):
    #     """ Create a new experiment """
    #     self.create_textbox_widget()
    # 
    #     # Create a UUID for the experiment
    #     exp_uuid = uuid.uuid4()
    # 
    #     # Create a directory for the new experiment
    #     create_experiment_directory_exception = directory.create_exp_directory(exp_uuid, self.current_nb_uuid)
    # 
    #     if not create_experiment_directory_exception:
    #         # Add the new experiment in the database
    #         create_experiment_database_exception = database.create_experiment(self.current_exp_name,
    #                                                                           exp_uuid,
    #                                                                           self.current_exp_objective,
    #                                                                           self.current_nb_uuid)
    # 
    #         if not create_experiment_database_exception:
    #             write_experiment_exception = experiment.write_experiment(exp_uuid,
    #                                                                      self.current_nb_uuid,
    #                                                                      self.current_exp_body)
    #             if not write_experiment_exception:
    #                 # Add the experiment to the experiment list
    #                 self.show_experiment_list()
    #     # Show a messagebox if an error happen during the experiment directory creation
    #     else:
    #         message = QMessageBox()
    #         message.setWindowTitle("LabNote")
    #         message.setText("Cannot create notebook")
    #         message.setInformativeText("An error occurred during the experiment directory creation.")
    #         message.setDetailedText(str(create_experiment_directory_exception))
    #         message.setIcon(QMessageBox.Warning)
    #         message.setStandardButtons(QMessageBox.Ok)
    #         message.exec()
    # 
    # def experiment_changed(self):
    #     """ Load the experiment informations when an experiment is selected from the list """
    # 
    #     # Update the current selected notebook uuid
    #     self.current_exp_uuid = self.lst_entry.currentItem().data(Qt.UserRole)
    # 
    #     self.create_textbox_widget()
    #     ret = experiment.open_experiment(self.current_nb_uuid, self.current_exp_uuid)
    # 
    #     if ret.dct:
    #         self.textbox_widget.title_text_edit.setPlainText(ret.dct['name'])
    #         self.textbox_widget.objectives_text_edit.setPlainText(ret.dct['objective'])
    #         self.textbox_widget.textedit.setHtml(ret.dct['body'])
    #     elif ret.error:
    #         message = QMessageBox()
    #         message.setWindowTitle("LabNote")
    #         message.setText("Error getting the experiment informations")
    #         message.setInformativeText("An error occurred while getting the experiment informations.")
    #         message.setDetailedText(str(ret.error))
    #         message.setIcon(QMessageBox.Warning)
    #         message.setStandardButtons(QMessageBox.Ok)
    #         message.exec()
    # 
    # def show_experiment_list(self):
    #     """ Show the list of experiment for the open notebook. """
    #     # Clear the existing list
    #     self.lst_entry.clear()
    # 
    #     # Get experiment list
    #     ret = database.get_experiment_list_notebook(self.current_nb_uuid)
    # 
    #     if ret.lst:
    #         # Add all experiments to the list widget
    #         for item in ret.lst:
    #             # Create experiment widget
    #             list_widget_item = QListWidgetItem()
    #             widget = list_widget.ListWidget()
    #             widget.set_title(item['name'])
    #             widget.set_subtitle(item['objective'])
    # 
    #             list_widget_item.setData(Qt.UserRole, item['uuid'])
    # 
    #             # Add widget to list
    #             list_widget_item.setSizeHint(widget.sizeHint())
    #             self.lst_entry.addItem(list_widget_item)
    #             self.lst_entry.setItemWidget(list_widget_item, widget)
    # 
    #             self.lst_entry.setCurrentRow(0)
    # 
    #             # Update the current selected notebook uuid
    #             self.current_exp_uuid = self.lst_entry.currentItem().data(Qt.UserRole)
    #     elif ret.error:
    #         message = QMessageBox()
    #         message.setWindowTitle("LabNote")
    #         message.setText("Error getting the experiment list")
    #         message.setInformativeText("An error occurred while getting the experiment list. ")
    #         message.setDetailedText(str(ret.error))
    #         message.setIcon(QMessageBox.Warning)
    #         message.setStandardButtons(QMessageBox.Ok)
    #         message.exec()
    # 
    # def create_textbox_widget(self):
    #     """ Create the textbox widget when an experiment is selected for the first time """
    #     if self.centralWidget().layout().indexOf(self.no_entry_widget) != -1:
    #         self.textbox_widget = textbox.Textbox()
    #         self.centralWidget().layout().removeWidget(self.no_entry_widget)
    #         self.no_entry_widget.deleteLater()
    #         self.no_entry_widget = None
    # 
    #         self.centralWidget().layout().addWidget(self.textbox_widget)
    #         self.centralWidget().layout().setStretch(2, 10)
    # 
    #         # Connect slots
    #         self.textbox_widget.title_text_edit.textChanged.connect(self.title_changed)
    #         self.textbox_widget.objectives_text_edit.textChanged.connect(self.objective_changed)
    #         self.textbox_widget.textedit.textChanged.connect(self.body_changed)
    # 
    # def save_experiment(self):
    #     """ Save the current experiment """
    #     update_exception = experiment.save_experiment(self.current_nb_uuid, self.current_exp_uuid, self.current_exp_name,
    #                                                   self.current_exp_objective, self.current_exp_body)
    # 
    #     self.name_updated = False
    #     self.objective_updated = False
    #     self.body_updated = False
    # 
    #     if update_exception:
    #         message = QMessageBox()
    #         message.setWindowTitle("LabNote")
    #         message.setText("Error saving the experiment")
    #         message.setInformativeText("An error occurred while saving the experiment to the database.")
    #         message.setDetailedText(str(update_exception))
    #         message.setIcon(QMessageBox.Warning)
    #         message.setStandardButtons(QMessageBox.Ok)
    #         message.exec()
    # 
    # def title_changed(self):
    #     """ Update the current title """
    # 
    #     # Set the current experiment name
    #     self.current_exp_name = self.textbox_widget.title_text_edit.toPlainText()
    #     self.name_updated = True
    # 
    #     # Update the current item title in the experiment list
    #     widget = self.lst_entry.itemWidget(self.lst_entry.currentItem())
    #     widget.set_title(self.current_exp_name)
    # 
    # def objective_changed(self):
    #     """ Update the current objective """
    # 
    #     # Set the current experiment objective
    #     self.current_exp_objective = self.textbox_widget.objectives_text_edit.toPlainText()
    #     self.objective_updated = True
    # 
    #     # Update the current item objective in the experiment list
    #     widget = self.lst_entry.itemWidget(self.lst_entry.currentItem())
    #     widget.set_subtitle(self.current_exp_objective)
    # 
    # def body_changed(self):
    #     """ Update the current body """
    #     self.current_exp_body = self.textbox_widget.textedit.toHtml()
    #     self.body_updated = True


class ProjectNotebookTreeView(TreeView):
    """ This class manage the data in the project and notebook tree widget """

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
