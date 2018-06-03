# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/SDR Soft/LabNote/LabNote/ui/qt_ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(738, 491)
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame = QtWidgets.QFrame(self.central_widget)
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
        self.lbl_notebook.setFont(font)
        self.lbl_notebook.setStyleSheet("font: \"Al Bayan\"")
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
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.frame_layout.addItem(spacerItem)
        self.btn_add_notebook = QtWidgets.QPushButton(self.frame)
        self.btn_add_notebook.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily(".SF NS Text")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.btn_add_notebook.setFont(font)
        self.btn_add_notebook.setToolTip("")
        self.btn_add_notebook.setStyleSheet("")
        self.btn_add_notebook.setFlat(False)
        self.btn_add_notebook.setObjectName("btn_add_notebook")
        self.frame_layout.addWidget(self.btn_add_notebook)
        self.verticalLayout.addLayout(self.frame_layout)
        self.horizontalLayout_2.addWidget(self.frame)
        self.lst_entry = QtWidgets.QListView(self.central_widget)
        self.lst_entry.setMinimumSize(QtCore.QSize(250, 0))
        self.lst_entry.setMaximumSize(QtCore.QSize(250, 16777215))
        self.lst_entry.setAutoFillBackground(False)
        self.lst_entry.setStyleSheet("")
        self.lst_entry.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lst_entry.setObjectName("lst_entry")
        self.horizontalLayout_2.addWidget(self.lst_entry)
        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 738, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lbl_notebook.setText(_translate("MainWindow", "Notebook"))
        self.btn_add_notebook.setText(_translate("MainWindow", "+"))

