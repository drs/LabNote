# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QtCore.QSize(700, 450))
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(self.central_widget)
        self.frame.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.frame.setFont(font)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_notebook = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily(".SF NS Text")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.lbl_notebook.setFont(font)
        self.lbl_notebook.setStyleSheet("")
        self.lbl_notebook.setObjectName("lbl_notebook")
        self.verticalLayout.addWidget(self.lbl_notebook)
        self.lst_notebook = QtWidgets.QListWidget(self.frame)
        self.lst_notebook.setMinimumSize(QtCore.QSize(190, 0))
        self.lst_notebook.setMaximumSize(QtCore.QSize(190, 16777215))
        self.lst_notebook.setObjectName("lst_notebook")
        self.verticalLayout.addWidget(self.lst_notebook)
        self.frame_layout = QtWidgets.QHBoxLayout()
        self.frame_layout.setSpacing(0)
        self.frame_layout.setObjectName("frame_layout")
        self.btn_add_notebook = QtWidgets.QPushButton(self.frame)
        self.btn_add_notebook.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily(".SF NS Text")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.btn_add_notebook.setFont(font)
        self.btn_add_notebook.setStyleSheet("")
        self.btn_add_notebook.setFlat(False)
        self.btn_add_notebook.setObjectName("btn_add_notebook")
        self.frame_layout.addWidget(self.btn_add_notebook)
        self.btn_settings = QtWidgets.QPushButton(self.frame)
        self.btn_settings.setMinimumSize(QtCore.QSize(0, 0))
        self.btn_settings.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.btn_settings.setText("")
        self.btn_settings.setIconSize(QtCore.QSize(16, 16))
        self.btn_settings.setFlat(True)
        self.btn_settings.setObjectName("btn_settings")
        self.frame_layout.addWidget(self.btn_settings)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.frame_layout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.frame_layout)
        self.horizontalLayout.addWidget(self.frame)
        self.entry_frame = QtWidgets.QFrame(self.central_widget)
        self.entry_frame.setMinimumSize(QtCore.QSize(250, 0))
        self.entry_frame.setMaximumSize(QtCore.QSize(250, 16777215))
        self.entry_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.entry_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.entry_frame.setObjectName("entry_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.entry_frame)
        self.horizontalLayout_2.setContentsMargins(10, 0, 10, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lst_entry = QtWidgets.QListWidget(self.entry_frame)
        self.lst_entry.setMinimumSize(QtCore.QSize(230, 0))
        self.lst_entry.setMaximumSize(QtCore.QSize(230, 16777215))
        self.lst_entry.setAutoFillBackground(False)
        self.lst_entry.setStyleSheet("")
        self.lst_entry.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lst_entry.setObjectName("lst_entry")
        self.horizontalLayout_2.addWidget(self.lst_entry)
        self.horizontalLayout.addWidget(self.entry_frame)
        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuNotebook = QtWidgets.QMenu(self.menubar)
        self.menuNotebook.setObjectName("menuNotebook")
        self.menuExperiment = QtWidgets.QMenu(self.menubar)
        self.menuExperiment.setObjectName("menuExperiment")
        self.menuData = QtWidgets.QMenu(self.menubar)
        self.menuData.setObjectName("menuData")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.experiment_toolbar = QtWidgets.QToolBar(MainWindow)
        self.experiment_toolbar.setMovable(False)
        self.experiment_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.experiment_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.experiment_toolbar.setFloatable(False)
        self.experiment_toolbar.setObjectName("experiment_toolbar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.experiment_toolbar)
        self.data_toolbar = QtWidgets.QToolBar(MainWindow)
        self.data_toolbar.setMovable(False)
        self.data_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.data_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.data_toolbar.setFloatable(False)
        self.data_toolbar.setObjectName("data_toolbar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.data_toolbar)
        self.search_toolbar = QtWidgets.QToolBar(MainWindow)
        self.search_toolbar.setMovable(False)
        self.search_toolbar.setAllowedAreas(QtCore.Qt.NoToolBarArea)
        self.search_toolbar.setFloatable(False)
        self.search_toolbar.setObjectName("search_toolbar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.search_toolbar)
        self.act_new = QtWidgets.QAction(MainWindow)
        self.act_new.setObjectName("act_new")
        self.act_duplicate = QtWidgets.QAction(MainWindow)
        self.act_duplicate.setObjectName("act_duplicate")
        self.act_share = QtWidgets.QAction(MainWindow)
        self.act_share.setObjectName("act_share")
        self.act_new_experiment = QtWidgets.QAction(MainWindow)
        self.act_new_experiment.setObjectName("act_new_experiment")
        self.actionExport_as_PDF = QtWidgets.QAction(MainWindow)
        self.actionExport_as_PDF.setObjectName("actionExport_as_PDF")
        self.actionNew_notebook = QtWidgets.QAction(MainWindow)
        self.actionNew_notebook.setObjectName("actionNew_notebook")
        self.actionEdit_notebook = QtWidgets.QAction(MainWindow)
        self.actionEdit_notebook.setObjectName("actionEdit_notebook")
        self.actionDelete_notebook = QtWidgets.QAction(MainWindow)
        self.actionDelete_notebook.setObjectName("actionDelete_notebook")
        self.actionNew_experiment_2 = QtWidgets.QAction(MainWindow)
        self.actionNew_experiment_2.setObjectName("actionNew_experiment_2")
        self.actionDuplicate_experiment = QtWidgets.QAction(MainWindow)
        self.actionDuplicate_experiment.setObjectName("actionDuplicate_experiment")
        self.act_protocols = QtWidgets.QAction(MainWindow)
        self.act_protocols.setObjectName("act_protocols")
        self.act_dataset = QtWidgets.QAction(MainWindow)
        self.act_dataset.setObjectName("act_dataset")
        self.act_project = QtWidgets.QAction(MainWindow)
        self.act_project.setObjectName("act_project")
        self.act_library = QtWidgets.QAction(MainWindow)
        self.act_library.setObjectName("act_library")
        self.act_samples = QtWidgets.QAction(MainWindow)
        self.act_samples.setObjectName("act_samples")
        self.menuFile.addAction(self.act_new_experiment)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExport_as_PDF)
        self.menuNotebook.addAction(self.actionNew_notebook)
        self.menuNotebook.addAction(self.actionEdit_notebook)
        self.menuNotebook.addSeparator()
        self.menuNotebook.addAction(self.actionDelete_notebook)
        self.menuExperiment.addAction(self.actionNew_experiment_2)
        self.menuExperiment.addAction(self.actionDuplicate_experiment)
        self.menuData.addAction(self.act_protocols)
        self.menuData.addAction(self.act_dataset)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuNotebook.menuAction())
        self.menubar.addAction(self.menuExperiment.menuAction())
        self.menubar.addAction(self.menuData.menuAction())
        self.experiment_toolbar.addAction(self.act_project)
        self.experiment_toolbar.addAction(self.act_new)
        self.experiment_toolbar.addAction(self.act_duplicate)
        self.data_toolbar.addAction(self.act_share)
        self.data_toolbar.addAction(self.act_protocols)
        self.data_toolbar.addAction(self.act_library)
        self.data_toolbar.addAction(self.act_dataset)
        self.search_toolbar.addAction(self.act_samples)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lbl_notebook.setText(_translate("MainWindow", "Notebook"))
        self.btn_add_notebook.setToolTip(_translate("MainWindow", "Create a new notebook"))
        self.btn_add_notebook.setText(_translate("MainWindow", "+"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuNotebook.setTitle(_translate("MainWindow", "Notebook"))
        self.menuExperiment.setTitle(_translate("MainWindow", "Experiment"))
        self.menuData.setTitle(_translate("MainWindow", "Data"))
        self.experiment_toolbar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.data_toolbar.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.search_toolbar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.act_new.setText(_translate("MainWindow", "New"))
        self.act_new.setToolTip(_translate("MainWindow", "New experiment"))
        self.act_duplicate.setText(_translate("MainWindow", "Duplicate"))
        self.act_duplicate.setToolTip(_translate("MainWindow", "Duplicate the current experiment"))
        self.act_share.setText(_translate("MainWindow", "Share"))
        self.act_share.setToolTip(_translate("MainWindow", "Share as PDF"))
        self.act_new_experiment.setText(_translate("MainWindow", "New experiment"))
        self.actionExport_as_PDF.setText(_translate("MainWindow", "Export as PDF"))
        self.actionNew_notebook.setText(_translate("MainWindow", "New notebook"))
        self.actionEdit_notebook.setText(_translate("MainWindow", "Edit notebook"))
        self.actionDelete_notebook.setText(_translate("MainWindow", "Delete notebook"))
        self.actionNew_experiment_2.setText(_translate("MainWindow", "New experiment"))
        self.actionDuplicate_experiment.setText(_translate("MainWindow", "Duplicate experiment"))
        self.act_protocols.setText(_translate("MainWindow", "Protocols"))
        self.act_protocols.setToolTip(_translate("MainWindow", "Open protocole window"))
        self.act_dataset.setText(_translate("MainWindow", "Dataset"))
        self.act_dataset.setToolTip(_translate("MainWindow", "Open dataset window"))
        self.act_project.setText(_translate("MainWindow", "Project"))
        self.act_project.setToolTip(_translate("MainWindow", "Open the project window"))
        self.act_library.setText(_translate("MainWindow", "Library"))
        self.act_library.setToolTip(_translate("MainWindow", "Open library"))
        self.act_samples.setText(_translate("MainWindow", "Samples"))
        self.act_samples.setToolTip(_translate("MainWindow", "Open samples"))

