# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/SDR Soft/LabNote/LabNote/ui/qt_ui/new_notebook.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewNotebook(object):
    def setupUi(self, NewNotebook):
        NewNotebook.setObjectName("NewNotebook")
        NewNotebook.resize(450, 137)
        NewNotebook.setMinimumSize(QtCore.QSize(0, 0))
        NewNotebook.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(NewNotebook)
        self.horizontalLayout_2.setContentsMargins(12, 12, 12, 12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbl_picture = QtWidgets.QLabel(NewNotebook)
        self.lbl_picture.setMinimumSize(QtCore.QSize(64, 64))
        self.lbl_picture.setMaximumSize(QtCore.QSize(64, 64))
        self.lbl_picture.setText("")
        self.lbl_picture.setObjectName("lbl_picture")
        self.horizontalLayout_2.addWidget(self.lbl_picture)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_new_notebook = QtWidgets.QLabel(NewNotebook)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_new_notebook.setFont(font)
        self.lbl_new_notebook.setObjectName("lbl_new_notebook")
        self.verticalLayout.addWidget(self.lbl_new_notebook)
        self.lbl_name = QtWidgets.QLabel(NewNotebook)
        self.lbl_name.setObjectName("lbl_name")
        self.verticalLayout.addWidget(self.lbl_name)
        self.txt_name = QtWidgets.QLineEdit(NewNotebook)
        self.txt_name.setObjectName("txt_name")
        self.verticalLayout.addWidget(self.txt_name)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_cancel = QtWidgets.QPushButton(NewNotebook)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.btn_create = QtWidgets.QPushButton(NewNotebook)
        self.btn_create.setEnabled(False)
        self.btn_create.setObjectName("btn_create")
        self.horizontalLayout.addWidget(self.btn_create)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(NewNotebook)
        QtCore.QMetaObject.connectSlotsByName(NewNotebook)

    def retranslateUi(self, NewNotebook):
        _translate = QtCore.QCoreApplication.translate
        NewNotebook.setWindowTitle(_translate("NewNotebook", "Dialog"))
        self.lbl_new_notebook.setText(_translate("NewNotebook", "New Notebook"))
        self.lbl_name.setText(_translate("NewNotebook", "Enter a name for the new notebook :  "))
        self.txt_name.setPlaceholderText(_translate("NewNotebook", "Notebook name"))
        self.btn_cancel.setText(_translate("NewNotebook", "Cancel"))
        self.btn_create.setText(_translate("NewNotebook", "Create"))

