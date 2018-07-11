# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/dialog/notebook.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Notebook(object):
    def setupUi(self, Notebook):
        Notebook.setObjectName("Notebook")
        Notebook.resize(450, 173)
        Notebook.setMinimumSize(QtCore.QSize(0, 0))
        Notebook.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Notebook)
        self.horizontalLayout_2.setContentsMargins(12, 12, 12, 12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbl_picture = QtWidgets.QLabel(Notebook)
        self.lbl_picture.setMinimumSize(QtCore.QSize(64, 64))
        self.lbl_picture.setMaximumSize(QtCore.QSize(64, 64))
        self.lbl_picture.setText("")
        self.lbl_picture.setObjectName("lbl_picture")
        self.horizontalLayout_2.addWidget(self.lbl_picture)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_title = QtWidgets.QLabel(Notebook)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setObjectName("lbl_title")
        self.verticalLayout.addWidget(self.lbl_title)
        self.lbl_name = QtWidgets.QLabel(Notebook)
        self.lbl_name.setObjectName("lbl_name")
        self.verticalLayout.addWidget(self.lbl_name)
        self.txt_name = QtWidgets.QLineEdit(Notebook)
        self.txt_name.setObjectName("txt_name")
        self.verticalLayout.addWidget(self.txt_name)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(Notebook)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.cbx_project = QtWidgets.QComboBox(Notebook)
        self.cbx_project.setObjectName("cbx_project")
        self.horizontalLayout_3.addWidget(self.cbx_project)
        self.horizontalLayout_3.setStretch(1, 5)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_cancel = QtWidgets.QPushButton(Notebook)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.btn_create = QtWidgets.QPushButton(Notebook)
        self.btn_create.setEnabled(False)
        self.btn_create.setObjectName("btn_create")
        self.horizontalLayout.addWidget(self.btn_create)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Notebook)
        QtCore.QMetaObject.connectSlotsByName(Notebook)

    def retranslateUi(self, Notebook):
        _translate = QtCore.QCoreApplication.translate
        Notebook.setWindowTitle(_translate("Notebook", "Dialog"))
        self.lbl_title.setText(_translate("Notebook", "Create a notebook"))
        self.lbl_name.setText(_translate("Notebook", "Enter a name for the new notebook :  "))
        self.txt_name.setPlaceholderText(_translate("Notebook", "Notebook name"))
        self.label.setText(_translate("Notebook", "Project : "))
        self.btn_cancel.setText(_translate("Notebook", "Cancel"))
        self.btn_create.setText(_translate("Notebook", "Create"))

