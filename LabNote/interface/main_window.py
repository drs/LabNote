"""
This module contain the classes responsible for launching and managing the LabNote MainWindow.
"""

# Python import
import uuid
import sys
import sqlite3

# PyQt import
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QLabel, QListWidgetItem, QLineEdit, QAction, \
    QSizePolicy, QMenu
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QSettings, QByteArray

# Project import
from labnote.ui.ui_mainwindow import Ui_MainWindow
from labnote.core import stylesheet, list_widget
from labnote.utils import database, directory, experiment, fsentry
from labnote.interface import textbox, project, library
from labnote.interface.new_notebook import NewNotebook
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.resources import resources


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

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()

        # Read program settings
        self.read_settings()

        # Check files integrity
        self.check_integrity()

        # Show existing notebook list
        self.show_notebook_list()

    def init_ui(self):
        """ Initialize all the GUI elements """

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

        # Set search widget in toolbar
        search_icon = QIcon(":/Icons/MainWindow/icons/main-window/search.png")

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
        self.notebook_setting_menu.addAction(self.act_delete_notebook)
        self.act_rename_notebook = QAction("Rename notebook", self)
        self.act_rename_notebook.triggered.connect(self.start_rename_notebook)
        self.notebook_setting_menu.addAction(self.act_rename_notebook)
        self.btn_settings.setMenu(self.notebook_setting_menu)

        # Disable the notebook and experiment related actions from toolbar
        self.act_new.setEnabled(False)
        self.act_new_experiment.setEnabled(False)
        self.act_share.setEnabled(False)
        self.act_duplicate.setEnabled(False)

        # Remove focus rectangle
        self.lst_notebook.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.lst_entry.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Set no entry widget as default widget
        self.set_no_entry_widget()

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/main_window.qss")

        # Slots connection
        self.btn_add_notebook.clicked.connect(self.open_new_notebook_dialog)
        self.lst_notebook.itemSelectionChanged.connect(self.notebook_changed)
        self.act_new.triggered.connect(self.create_experiment)
        self.act_new_experiment.triggered.connect(self.create_experiment)
        self.lst_entry.itemSelectionChanged.connect(self.experiment_changed)
        self.act_project.triggered.connect(self.open_project)
        self.act_library.triggered.connect(self.open_library)

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

    def set_no_entry_widget(self):
        """ Show a no entry selected label when no entry or notebook are open. """

        # Setting up widget elements
        no_entry_pixmap = QPixmap(":/Icons/MainWindow/icons/main-window/no_entry_selected.png")
        lbl_no_entry_image = QLabel()
        lbl_no_entry_image.setAlignment(Qt.AlignCenter)

        lbl_no_entry_image.setPixmap(no_entry_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        lbl_no_entry_image.show()

        lbl_no_entry = QLabel("No entry selected")
        lbl_no_entry.setAlignment(Qt.AlignCenter)
        stylesheet.set_style_sheet(lbl_no_entry, ":/StyleSheet/style-sheet/main-window/no_entry_label.qss")

        # Setting up the layout
        self.no_entry_widget = QWidget()
        main_layout = QVBoxLayout(self.no_entry_widget)
        main_layout.addWidget(lbl_no_entry_image)
        main_layout.addWidget(lbl_no_entry)

        # Add widget to mainwindow
        self.centralWidget().layout().addWidget(self.no_entry_widget, Qt.AlignHCenter, Qt.AlignCenter)

    def check_integrity(self):
        """ Check if the main directory and database exist """
        try:
            fsentry.check_integrity()
        except (sqlite3.Error, OSError) as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unexpected error occured")
            message.setInformativeText("An unexpected error occurred while checking the main directory integrity "
                                       "The program will now close.")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

            fsentry.cleanup_main_directory()

            sys.exit("Unexpected error while checking the main directory integrity")

    """
    Toolbar functions
    """

    def open_project(self):
        """ Open the project dialog """
        project.Project(self)

    def open_library(self):
        """ Open the library dialog """
        library.Library(self)

    """
    Notebook list functions
    """
    def open_new_notebook_dialog(self):
        """ Show a sheet dialog that create a new notebook. """
        self.new_notebook = NewNotebook()
        self.new_notebook.setWindowModality(Qt.WindowModal)
        self.new_notebook.setParent(self, Qt.Sheet)
        self.new_notebook.show()
        self.new_notebook.accepted.connect(self.create_notebook)

    def create_notebook(self):
        """ Add a newly created notebook name to the notebook list. """
        # Get the notebook name
        nb_name = self.new_notebook.notebook_name
        proj_id = self.new_notebook.project_id

        try:
            fsentry.create_notebook(nb_name, proj_id)
        except (sqlite3.Error, OSError) as exception:
            message = QMessageBox(QMessageBox.Warning, "Cannot create notebook",
                                  "An error occurred during the notebook creation.", QMessageBox.Ok)
            message.setWindowTitle("LabNote")
            message.setDetailedText(str(exception))
            message.exec()

            return

        # Add the notebook to the notebook list
        self.show_notebook_list()

        # Select the newly inserted item
        items = self.lst_notebook.findItems(nb_name, Qt.MatchExactly)
        self.lst_notebook.setCurrentItem(items[0])

    def notebook_changed(self):
        """ Update the experiment list when the notebook change """
        self.current_nb_uuid = self.lst_notebook.currentItem().data(Qt.UserRole)

        self.show_experiment_list()

    def show_notebook_list(self, selected=None):
        """ Show the existing notebooks in the notebook list

        If the parameter selected is passed, this function can restore the last selected item.

        :param selected: Text of the last selected item
        :type selected: str
        """

        # Clear the existing list
        self.lst_notebook.clear()

        lst = None

        # Get the notebook list from the database
        try:
            lst = database.get_notebook_list()
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the notebook list")
            message.setInformativeText("An error occurred while getting the notebook list. ")
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

        if lst:
            # Add items to the list
            for notebook in lst:
                item = QListWidgetItem(notebook['name'])
                item.setData(Qt.UserRole, notebook['uuid'])
                self.lst_notebook.addItem(item)

            # Order the list
            self.lst_notebook.sortItems(Qt.AscendingOrder)
            self.lst_notebook.setCurrentRow(0)
            self.act_new.setEnabled(True)
            self.act_new_experiment.setEnabled(True)

            # Update the current selected notebook uuid
            self.current_nb_uuid = self.lst_notebook.currentItem().data(Qt.UserRole)

            self.show_experiment_list()

            # Sort item in ascending order
            self.lst_notebook.sortItems(Qt.AscendingOrder)

            # Select the last selected element
            if selected:
                item = self.lst_notebook.findItems(selected, Qt.MatchExactly)
                self.lst_notebook.setCurrentItem(item[0])

    def start_rename_notebook(self):
        """ Make a notebook item editable to allow renaming """
        current_row = self.lst_notebook.currentRow()
        # If an item is selected make it editable
        if current_row != -1:
            # Make the item editable
            item = self.lst_notebook.item(current_row)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

            index = self.lst_notebook.model().index(current_row, 0)
            self.lst_notebook.edit(index)

            self.call_finish_rename_notebook = lambda: self.finish_rename_notebook(current_row)

            # When the editing is finished call the function that rename the item in the database
            self.lst_notebook.itemDelegate().closeEditor.connect(self.call_finish_rename_notebook)

    def finish_rename_notebook(self, current_row):
        """ Change the notebook name in the database after editing is finished

        :param current_row: Row of the item being edited
        :type current_row: int
        """
        # Get the item at the row
        item = self.lst_notebook.item(current_row)

        # Set the item not editable
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)

        # Update notebook name in the database
        try:
            database.update_notebook(item.text(), item.data(Qt.UserRole))
        except sqlite3.Error as exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Cannot rename notebook")
            message.setInformativeText(
                "An error occurred while renaming the notebook {}.".format(item.text()))
            message.setDetailedText(str(exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

            return

        # Show the notebook list with the updated name
        self.show_notebook_list(selected=item.text())

        # Disconnect the slot
        # This is necessary to allow renaming of other notebook later on
        self.lst_notebook.itemDelegate().closeEditor.disconnect(self.call_finish_rename_notebook)

    def delete_notebook(self):
        """ Delete a notebook """
        # Get the notebook informations
        current_row = self.lst_notebook.currentRow()
        item = self.lst_notebook.item(current_row)
        nb_uuid = item.data(Qt.UserRole)
        nb_name = item.text()

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
                database.delete_notebook(nb_uuid)
                directory.delete_nb_directory(nb_uuid)
            except sqlite3.Error as exception:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Cannot delete notebook")
                message.setInformativeText("An error occurred while deleting the notebook in the database. The notebook"
                                           "was not deleted.")
                message.setDetailedText(str(exception))
                message.setIcon(QMessageBox.Warning)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()
            except OSError as exception:
                message = QMessageBox()
                message.setWindowTitle("LabNote")
                message.setText("Cannot delete notebook")
                message.setInformativeText("An error occurred while deleting the notebook {} directory."
                                           .format(nb_uuid))
                message.setDetailedText(str(exception))
                message.setIcon(QMessageBox.Warning)
                message.setStandardButtons(QMessageBox.Ok)
                message.exec()

        self.show_notebook_list()

    """
    Experiment list functions
    """
    def create_experiment(self):
        """ Create a new experiment """
        self.create_textbox_widget()

        # Create a UUID for the experiment
        exp_uuid = uuid.uuid4()

        # Create a directory for the new experiment
        create_experiment_directory_exception = directory.create_exp_directory(exp_uuid, self.current_nb_uuid)

        if not create_experiment_directory_exception:
            # Add the new experiment in the database
            create_experiment_database_exception = database.create_experiment(self.current_exp_name,
                                                                              exp_uuid,
                                                                              self.current_exp_objective,
                                                                              self.current_nb_uuid)

            if not create_experiment_database_exception:
                write_experiment_exception = experiment.write_experiment(exp_uuid,
                                                                         self.current_nb_uuid,
                                                                         self.current_exp_body)
                if not write_experiment_exception:
                    # Add the experiment to the experiment list
                    self.show_experiment_list()
        # Show a messagebox if an error happen during the experiment directory creation
        else:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Cannot create notebook")
            message.setInformativeText("An error occurred during the experiment directory creation.")
            message.setDetailedText(str(create_experiment_directory_exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def experiment_changed(self):
        """ Load the experiment informations when an experiment is selected from the list """

        # Update the current selected notebook uuid
        self.current_exp_uuid = self.lst_entry.currentItem().data(Qt.UserRole)

        self.create_textbox_widget()
        ret = experiment.open_experiment(self.current_nb_uuid, self.current_exp_uuid)

        if ret.dct:
            self.textbox_widget.title_text_edit.setPlainText(ret.dct['name'])
            self.textbox_widget.objectives_text_edit.setPlainText(ret.dct['objective'])
            self.textbox_widget.textedit.setHtml(ret.dct['body'])
        elif ret.error:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the experiment informations")
            message.setInformativeText("An error occurred while getting the experiment informations.")
            message.setDetailedText(str(ret.error))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def show_experiment_list(self):
        """ Show the list of experiment for the open notebook. """
        # Clear the existing list
        self.lst_entry.clear()

        # Get experiment list
        ret = database.get_experiment_list_notebook(self.current_nb_uuid)

        if ret.lst:
            # Add all experiments to the list widget
            for item in ret.lst:
                # Create experiment widget
                list_widget_item = QListWidgetItem()
                widget = list_widget.ListWidget()
                widget.set_title(item['name'])
                widget.set_subtitle(item['objective'])

                list_widget_item.setData(Qt.UserRole, item['uuid'])

                # Add widget to list
                list_widget_item.setSizeHint(widget.sizeHint())
                self.lst_entry.addItem(list_widget_item)
                self.lst_entry.setItemWidget(list_widget_item, widget)

                self.lst_entry.setCurrentRow(0)

                # Update the current selected notebook uuid
                self.current_exp_uuid = self.lst_entry.currentItem().data(Qt.UserRole)
        elif ret.error:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the experiment list")
            message.setInformativeText("An error occurred while getting the experiment list. ")
            message.setDetailedText(str(ret.error))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def create_textbox_widget(self):
        """ Create the textbox widget when an experiment is selected for the first time """
        if self.centralWidget().layout().indexOf(self.no_entry_widget) != -1:
            self.textbox_widget = textbox.Textbox()
            self.centralWidget().layout().removeWidget(self.no_entry_widget)
            self.no_entry_widget.deleteLater()
            self.no_entry_widget = None

            self.centralWidget().layout().addWidget(self.textbox_widget)
            self.centralWidget().layout().setStretch(2, 10)

            # Connect slots
            self.textbox_widget.title_text_edit.textChanged.connect(self.title_changed)
            self.textbox_widget.objectives_text_edit.textChanged.connect(self.objective_changed)
            self.textbox_widget.textedit.textChanged.connect(self.body_changed)

    def save_experiment(self):
        """ Save the current experiment """
        update_exception = experiment.save_experiment(self.current_nb_uuid, self.current_exp_uuid, self.current_exp_name,
                                                      self.current_exp_objective, self.current_exp_body)

        self.name_updated = False
        self.objective_updated = False
        self.body_updated = False

        if update_exception:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error saving the experiment")
            message.setInformativeText("An error occurred while saving the experiment to the database.")
            message.setDetailedText(str(update_exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def title_changed(self):
        """ Update the current title """

        # Set the current experiment name
        self.current_exp_name = self.textbox_widget.title_text_edit.toPlainText()
        self.name_updated = True

        # Update the current item title in the experiment list
        widget = self.lst_entry.itemWidget(self.lst_entry.currentItem())
        widget.set_title(self.current_exp_name)

    def objective_changed(self):
        """ Update the current objective """

        # Set the current experiment objective
        self.current_exp_objective = self.textbox_widget.objectives_text_edit.toPlainText()
        self.objective_updated = True

        # Update the current item objective in the experiment list
        widget = self.lst_entry.itemWidget(self.lst_entry.currentItem())
        widget.set_subtitle(self.current_exp_objective)

    def body_changed(self):
        """ Update the current body """
        self.current_exp_body = self.textbox_widget.textedit.toHtml()
        self.body_updated = True
