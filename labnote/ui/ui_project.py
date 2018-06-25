# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/project.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Project(object):
    def setupUi(self, Project):
        Project.setObjectName("Project")
        Project.resize(594, 443)
        self.verticalLayout = QtWidgets.QVBoxLayout(Project)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl_title = QtWidgets.QLabel(Project)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setObjectName("lbl_title")
        self.horizontalLayout.addWidget(self.lbl_title)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.txt_search = QtWidgets.QLineEdit(Project)
        self.txt_search.setObjectName("txt_search")
        self.horizontalLayout.addWidget(self.txt_search)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.table = QtWidgets.QTableWidget(Project)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.verticalLayout.addWidget(self.table)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(12, 6, 12, 12)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btn_close = QtWidgets.QPushButton(Project)
        self.btn_close.setAutoDefault(False)
        self.btn_close.setDefault(False)
        self.btn_close.setObjectName("btn_close")
        self.horizontalLayout_2.addWidget(self.btn_close)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Project)
        QtCore.QMetaObject.connectSlotsByName(Project)
        Project.setTabOrder(self.table, self.txt_search)
        Project.setTabOrder(self.txt_search, self.btn_close)

    def retranslateUi(self, Project):
        _translate = QtCore.QCoreApplication.translate
        Project.setWindowTitle(_translate("Project", "Form"))
        self.lbl_title.setText(_translate("Project", "Project"))
        self.txt_search.setPlaceholderText(_translate("Project", "Search"))
        self.btn_close.setText(_translate("Project", "Close"))

