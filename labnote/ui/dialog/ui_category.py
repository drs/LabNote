# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/dialog/category.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Category(object):
    def setupUi(self, Category):
        Category.setObjectName("Category")
        Category.resize(400, 133)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Category.sizePolicy().hasHeightForWidth())
        Category.setSizePolicy(sizePolicy)
        Category.setMinimumSize(QtCore.QSize(400, 133))
        self.verticalLayout = QtWidgets.QVBoxLayout(Category)
        self.verticalLayout.setContentsMargins(12, 12, 8, 8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, -1, 4, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lbl_title = QtWidgets.QLabel(Category)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setObjectName("lbl_title")
        self.verticalLayout_2.addWidget(self.lbl_title)
        self.lbl_name = QtWidgets.QLabel(Category)
        self.lbl_name.setObjectName("lbl_name")
        self.verticalLayout_2.addWidget(self.lbl_name)
        self.txt_name = QtWidgets.QLineEdit(Category)
        self.txt_name.setPlaceholderText("")
        self.txt_name.setObjectName("txt_name")
        self.verticalLayout_2.addWidget(self.txt_name)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_cancel = QtWidgets.QPushButton(Category)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.btn_create = QtWidgets.QPushButton(Category)
        self.btn_create.setEnabled(False)
        self.btn_create.setObjectName("btn_create")
        self.horizontalLayout.addWidget(self.btn_create)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Category)
        QtCore.QMetaObject.connectSlotsByName(Category)

    def retranslateUi(self, Category):
        _translate = QtCore.QCoreApplication.translate
        Category.setWindowTitle(_translate("Category", "Dialog"))
        self.lbl_title.setText(_translate("Category", "Category"))
        self.lbl_name.setText(_translate("Category", "Category name : "))
        self.btn_cancel.setText(_translate("Category", "Cancel"))
        self.btn_create.setText(_translate("Category", "Create"))

