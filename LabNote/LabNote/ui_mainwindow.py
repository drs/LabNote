# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/SDR Soft/P-LabNote/Source/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(738, 491)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.central_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.central_layout.setObjectName("central_layout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setMinimumSize(QtCore.QSize(150, 0))
        self.treeWidget.setMaximumSize(QtCore.QSize(150, 16777215))
        self.treeWidget.setStyleSheet("QTreeView:focus{ border: none; outline: none; }")
        self.treeWidget.setObjectName("treeWidget")
        self.verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_add_notebook = QtWidgets.QPushButton(self.centralwidget)
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
        self.horizontalLayout_2.addWidget(self.btn_add_notebook)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.central_layout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lst_entry = QtWidgets.QListView(self.centralwidget)
        self.lst_entry.setMinimumSize(QtCore.QSize(200, 0))
        self.lst_entry.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lst_entry.setAutoFillBackground(False)
        self.lst_entry.setStyleSheet("")
        self.lst_entry.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lst_entry.setObjectName("lst_entry")
        self.verticalLayout_2.addWidget(self.lst_entry)
        self.central_layout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
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
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Notebook"))
        self.btn_add_notebook.setText(_translate("MainWindow", "+"))

