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
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSettings, QByteArray

# Project import
from LabNote.ui.ui_mainwindow import Ui_MainWindow
from LabNote.common import stylesheet, sqlite_error, list_widget
from LabNote.data_management import integrity, database, directory, experiment
from LabNote.interface import textbox
from LabNote.interface.new_notebook import NewNotebook
from LabNote.resources import resources


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class responsible of launching the LabNote MainWindow interface.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/main_window.qss")

        # Set window title
        self.setWindowTitle("LabNote")

        # Unified toolbar on mac
        self.setUnifiedTitleAndToolBarOnMac(True)

        # Set toolbar icons
        self.act_new.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/new-experiment.png"))
        self.act_duplicate.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/duplicate.png"))
        self.act_share.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/share.png"))
        self.act_files.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/files.png"))
        self.act_dataset.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/dataset.png"))
        self.act_protocols.setIcon(QIcon(":/Icons/MainWindow/icons/main-window/protocols.png"))

        # Set toolbar separator
        empty_widget_1 = QWidget()
        empty_widget_1.setFixedWidth(190)
        self.experiment_toolbar.insertWidget(self.act_new, empty_widget_1)

        empty_widget_2 = QWidget()
        empty_widget_2.setFixedWidth(90)
        self.data_toolbar.insertWidget(self.act_protocols, empty_widget_2)

        empty_widget_3 = QWidget()
        empty_widget_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.search_toolbar.addWidget(empty_widget_3)

        # Set search widget in toolbar
        search_icon = QIcon(":/Icons/MainWindow/icons/main-window/search.png")

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search")
        self.txt_search.addAction(search_icon, QLineEdit.LeadingPosition)
        self.txt_search.setFixedWidth(300)
        self.search_toolbar.addWidget(self.txt_search)

        empty_widget_4 = QWidget()
        empty_widget_4.setFixedWidth(10)
        self.search_toolbar.addWidget(empty_widget_4)

        # Set notebook settings button menu
        self.notebook_setting_menu = QMenu(self)
        self.act_delete_notebook = QAction("Delete notebook", self)
        self.notebook_setting_menu.addAction(self.act_delete_notebook)
        self.btn_settings.setMenu(self.notebook_setting_menu)

        # Disable the notebook and experiment related actions from toolbar
        self.act_new.setEnabled(False)
        self.act_new_experiment.setEnabled(False)
        self.act_share.setEnabled(False)
        self.act_duplicate.setEnabled(False)

        # Remove focus rectangle
        self.lst_notebook.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.lst_entry.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.txt_search.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Set no entry widget as default widget
        self.set_no_entry_widget()

        # Read program settings
        self.read_settings()

        # Check files integrity
        self.check_files_integrity()

        # Show existing notebook list
        self.show_notebook_list()

        # Slots connection
        self.btn_add_notebook.clicked.connect(self.open_new_notebook_dialog)
        self.lst_notebook.currentItemChanged.connect(self.notebook_changed)
        self.act_new.triggered.connect(self.new_experiment)
        self.act_new_experiment.triggered.connect(self.new_experiment)

    @staticmethod
    def check_files_integrity():
        """ Check the program files integrity """
        exception = integrity.check_folder_integrity()

        # Main directory creation exception
        if exception[0] == integrity.MAIN_DIRECTORY_CREATION_EXCEPTION:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unexpected error during file structure creation")
            message.setInformativeText("An unexpected error occured during the creation of the file structure "
                                       "required to save the user information. "
                                       "The program will now close. Please delete any LabNote directory in Documents "
                                       "as it might interfere with a new program installation. "
                                       "The program will now close.")
            message.setDetailedText(str(exception[1]))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

            sys.exit("Unexpected error during main directory creation")

        # Main database creation exception
        elif exception[0] == integrity.MAIN_DATABASE_CREATION_EXCEPTION:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unexpected error during main database creation")
            message.setInformativeText("An unexpected error occurred during the creation of the main database. "
                                       "The program will now close.")
            message.setDetailedText(str(exception[1]))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

            sys.exit("Unexpected error during main database creation")

        elif exception[0] == integrity.PROTOCOLS_DATABASE_CREATION_EXCEPTION:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Unexpected error during protocol database creation")
            message.setInformativeText("An unexpected error occurred during the creation of the protocols database. "
                                       "The program will now close.")
            message.setDetailedText(str(exception[1]))
            message.setIcon(QMessageBox.Critical)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

            sys.exit("Unexpected error during protocol database creation")

    def show_notebook_list(self):
        """ Show the existing notebooks in the notebook list """

        # Clear the existing list
        self.lst_notebook.clear()

        # Get the notebook list from the database
        notebook_list = database.get_notebook_list()

        if not isinstance(notebook_list, sqlite3.Error):
            # Add items to the list
            for notebook in notebook_list:
                item = QListWidgetItem(notebook['name'])
                item.setData(Qt.UserRole, notebook['uuid'])
                self.lst_notebook.addItem(item)

            # Order the list
            self.lst_notebook.sortItems(Qt.AscendingOrder)
            self.lst_notebook.setCurrentRow(0)
            self.act_new.setEnabled(True)
            self.act_new_experiment.setEnabled(True)
            self.show_experiment_list()
        else:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Error getting the notebook list")
            message.setInformativeText("An error occurred while getting the notebook list. ")
            message.setDetailedText(str(notebook_list))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def read_settings(self):
        """ Read the setting when program launch to restore geometry and state """

        settings = QSettings("Samuel Drouin", "LabNote")
        self.restoreGeometry(settings.value("MainWindow/Geometry", QByteArray()))

    def closeEvent(self, e):
        """
        Write the program geometry and state to settings
        :param e: Close event
        :type e: QCloseEvent
        :returns: Event for the parent
        """

        settings = QSettings("Samuel Drouin", "LabNote")
        settings.setValue("MainWindow/Geometry", self.saveGeometry())

        return super(MainWindow, self).closeEvent(e)

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

    def open_new_notebook_dialog(self):
        """ Show a sheet dialog that create a new notebook. """

        self.new_notebook = NewNotebook()
        self.new_notebook.setWindowModality(Qt.WindowModal)
        self.new_notebook.setParent(self, Qt.Sheet)
        self.new_notebook.show()
        self.new_notebook.accepted.connect(self.create_notebook)

    def create_notebook(self):
        """ Add a newly created notebook name to the notebook list. """
        nb_name = self.new_notebook.notebook_name
        nb_uuid = uuid.uuid4()

        # Create a directory for the new notebook
        create_nb_directory_exception = directory.create_nb_directory(nb_uuid)

        if not create_nb_directory_exception:
            # Add the new notebook to the database
            create_notebook_exception = database.create_notebook(nb_name, nb_uuid)

            if not create_notebook_exception:
                # Add the notebook to the notebook list
                self.show_notebook_list()

                # Select the newly inserted item
                items = self.lst_notebook.findItems(nb_name, Qt.MatchExactly)
                self.lst_notebook.setCurrentItem(items[0])
            # Handle exception thrown during the notebook is added to the database
            else:
                # Delete the newly created notebook directory
                delete_nb_directory_exception = directory.delete_nb_directory(nb_uuid)

                # Show a messagebox that an error happened while the notebook was added to the database
                # and during the notebook directory deletion
                if delete_nb_directory_exception:
                    message = QMessageBox()
                    message.setWindowTitle("LabNote")
                    message.setText("Cannot create notebook")
                    message.setInformativeText(
                        "An error occurred during the notebook directory creation in the database and the associated"
                        "files could not be deleted. The notebook with UUID {} should be deleted "
                        "manually.".format(nb_uuid))
                    message.setDetailedText("Database exception : \n" + str(create_notebook_exception) + "\n" +
                                            "Directory deletion : \n" + str(delete_nb_directory_exception))
                    message.setIcon(QMessageBox.Warning)
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                # Show a messagebox that an error happened while the notebook was added to the database
                else:
                    error_code = sqlite_error.sqlite_err_handler(str(create_notebook_exception))

                    # Show a messagebox
                    # Show a unique contraint error
                    if error_code == sqlite_error.UNIQUE_CODE:
                        message = QMessageBox()
                        message.setWindowTitle("LabNote")
                        message.setText("Cannot create notebook")
                        message.setInformativeText("Another notebook with the same name already exist in the database. "
                                                   "Please choose another name.")
                        message.setIcon(QMessageBox.Warning)
                        message.setStandardButtons(QMessageBox.Ok)
                        message.exec()
                    else:
                        # Show the generic messagebox for unhandled errors
                        message = QMessageBox()
                        message.setWindowTitle("LabNote")
                        message.setText("Cannot create notebook")
                        message.setInformativeText("An error occurred during the notebook creation in the database.")
                        message.setDetailedText(str(create_notebook_exception))
                        message.setIcon(QMessageBox.Warning)
                        message.setStandardButtons(QMessageBox.Ok)
                        message.exec()
        # Show a messagebox if an error happen during the notebook directory creation
        else:
            message = QMessageBox()
            message.setWindowTitle("LabNote")
            message.setText("Cannot create notebook")
            message.setInformativeText("An error occurred during the notebook directory creation.")
            message.setDetailedText(str(create_nb_directory_exception))
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def notebook_changed(self, current, previous):
        """ Handle notebook changes :
            - Change the experiment list
            - Allow new experiment creation
        """

        # Allow new experiment creation
        #self.act_new.setEnabled(True)
        #self.act_new_experiment.setEnabled(True)

    def new_experiment(self):
        """ Create a new experiment """
        if self.centralWidget().layout().indexOf(self.no_entry_widget) != -1:
            self.textbox_widget = textbox.Textbox()
            self.centralWidget().layout().removeWidget(self.no_entry_widget)
            self.no_entry_widget.deleteLater()
            self.no_entry_widget = None

            self.centralWidget().layout().addWidget(self.textbox_widget)
            self.centralWidget().layout().setStretch(2, 10)

        # Create a UUID for the experiment
        exp_uuid = uuid.uuid4()

        # Create the experiment
        experiment.create_experiment(exp_uuid,
                                     self.lst_notebook.currentItem().data(Qt.UserRole),
                                     self.textbox_widget.textedit.toHtml(),
                                     self.textbox_widget.title_text_edit.toPlainText() or "Untitled experiment",
                                     self.textbox_widget.objectives_text_edit.toPlainText())

    def show_experiment_list(self):
        """ Show the list of experiment for the open notebook """
        # Clear the existing list
        self.lst_entry.clear()

        # Get experiment list
        lst = database.get_experiment_list_notebook(self.lst_notebook.currentItem().data(Qt.UserRole))
        for item in lst:
            # Create experiment widget
            list_widget_item = QListWidgetItem()

            widget = list_widget.ListWidget()
            widget.set_title(item['name'])

            # Add widget to list
            list_widget_item.setSizeHint(widget.sizeHint())
            self.lst_entry.addItem(list_widget_item)
            self.lst_entry.setItemWidget(list_widget_item, widget)

