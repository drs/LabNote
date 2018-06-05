"""
This module contain the classes responsible for launching and managing the LabNote MainWindow.
"""


from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSettings, QByteArray

from ui.ui_mainwindow import Ui_MainWindow
from common import style
from interface import textbox
from interface.new_notebook import NewNotebook
from resources import resources


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class responsible of launching the LabNote MainWindow interface.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Set style sheet
        style.set_style_sheet(self, ":/StyleSheet/style-sheet/main_window.qss")

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
        empty_widget_1.setMinimumWidth(190)
        self.experiment_toolbar.insertWidget(self.act_new, empty_widget_1)

        empty_widget_2 = QWidget()
        empty_widget_2.setMinimumWidth(90)
        self.data_toolbar.insertWidget(self.act_protocols, empty_widget_2)

        # Disable the notebook and experiment related actions from toolbar
        self.act_new.setEnabled(False)
        self.act_new_experiment.setEnabled(False)
        self.act_share.setEnabled(False)
        self.act_duplicate.setEnabled(False)

        # Remove focus rectangle
        self.lst_notebook.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.lst_entry.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Set no entry widget as default widget
        #self.set_no_entry_widget()
        self.new_experiment()

        # Read program settings
        self.read_settings()

        # Slots connection
        self.btn_add_notebook.clicked.connect(self.open_new_notebook_dialog)
        self.lst_notebook.currentItemChanged.connect(self.notebook_changed)
        self.act_new.triggered.connect(self.new_experiment)
        self.act_new_experiment.triggered.connect(self.new_experiment)

    def read_settings(self):
        """
        Read the setting when program launch to restore geometry and state
        """
        settings = QSettings("Samuel Drouin", "LabNote")
        self.restoreGeometry(settings.value("MainWindow/Geometry", QByteArray()))

    def closeEvent(self, e):
        """
        Write the program geometry and state to settings
        :param e: QCloseEvent
        """
        settings = QSettings("Samuel Drouin", "LabNote")
        settings.setValue("MainWindow/Geometry", self.saveGeometry())

        return super(MainWindow, self).closeEvent(e)

    def set_no_entry_widget(self):
        """
        Show a no entry selected label when no entry or notebook are open.
        """
        # Setting up widget elements
        no_entry_pixmap = QPixmap(":/Icons/MainWindow/icons/main-window/no_entry_selected.png")
        lbl_no_entry_image = QLabel()
        lbl_no_entry_image.setAlignment(Qt.AlignCenter)

        lbl_no_entry_image.setPixmap(no_entry_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        lbl_no_entry_image.show()

        lbl_no_entry = QLabel("No entry selected")
        lbl_no_entry.setAlignment(Qt.AlignCenter)
        style.set_style_sheet(lbl_no_entry, ":/StyleSheet/style-sheet/main-window/no_entry_label.qss")

        # Setting up the layout
        self.no_entry_widget = QWidget()
        main_layout = QVBoxLayout(self.no_entry_widget)
        main_layout.addWidget(lbl_no_entry_image)
        main_layout.addWidget(lbl_no_entry)

        # Add widget to mainwindow
        self.centralWidget().layout().addWidget(self.no_entry_widget, Qt.AlignHCenter, Qt.AlignCenter)

    def open_new_notebook_dialog(self):
        """
        Show a sheet dialog that create a new notebook.
        """
        self.new_notebook = NewNotebook()
        self.new_notebook.setWindowModality(Qt.WindowModal)
        self.new_notebook.setParent(self, Qt.Sheet)
        self.new_notebook.show()
        self.new_notebook.accepted.connect(self.add_notebook)

    def add_notebook(self):
        """
        Add a newly created notebook name to the notebook list.
        """
        notebook_name = self.new_notebook.notebook_name
        self.lst_notebook.addItem(notebook_name)
        self.lst_notebook.sortItems(Qt.AscendingOrder)

        # Select the newly inserted item
        items = self.lst_notebook.findItems(notebook_name, Qt.MatchExactly)
        self.lst_notebook.setCurrentItem(items[0])

    def notebook_changed(self, current, previous):
        """
        Handle notebook changes :
            - Change the experiment list
            - Allow new experiment creation
        """
        # Allow new experiment creation
        self.act_new.setEnabled(True)
        self.act_new_experiment.setEnabled(True)

    def new_experiment(self):
        """
        New exp
        :return:
        """
        #if self.centralWidget().layout().indexOf(self.no_entry_widget) != -1:
        textbox_widget = textbox.Textbox()
        #self.centralWidget().layout().removeWidget(self.no_entry_widget)
        #self.no_entry_widget.deleteLater()
        #self.no_entry_widget = None

        self.centralWidget().layout().addWidget(textbox_widget)
        self.centralWidget().layout().setStretch(2, 10)
