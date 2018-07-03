# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/dialog/subcategory.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Subcategory(object):
    def setupUi(self, Subcategory):
        Subcategory.setObjectName("Subcategory")
        Subcategory.resize(400, 169)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Subcategory.sizePolicy().hasHeightForWidth())
        Subcategory.setSizePolicy(sizePolicy)
        Subcategory.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout = QtWidgets.QVBoxLayout(Subcategory)
        self.verticalLayout.setContentsMargins(12, 12, 8, 8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, -1, 4, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lbl_title = QtWidgets.QLabel(Subcategory)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setObjectName("lbl_title")
        self.verticalLayout_2.addWidget(self.lbl_title)
        self.lbl_name = QtWidgets.QLabel(Subcategory)
        self.lbl_name.setObjectName("lbl_name")
        self.verticalLayout_2.addWidget(self.lbl_name)
        self.txt_name = QtWidgets.QLineEdit(Subcategory)
        self.txt_name.setPlaceholderText("")
        self.txt_name.setObjectName("txt_name")
        self.verticalLayout_2.addWidget(self.txt_name)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Subcategory)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.cbx_category = QtWidgets.QComboBox(Subcategory)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbx_category.sizePolicy().hasHeightForWidth())
        self.cbx_category.setSizePolicy(sizePolicy)
        self.cbx_category.setObjectName("cbx_category")
        self.horizontalLayout_2.addWidget(self.cbx_category)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_cancel = QtWidgets.QPushButton(Subcategory)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.btn_create = QtWidgets.QPushButton(Subcategory)
        self.btn_create.setEnabled(False)
        self.btn_create.setObjectName("btn_create")
        self.horizontalLayout.addWidget(self.btn_create)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Subcategory)
        QtCore.QMetaObject.connectSlotsByName(Subcategory)

    def retranslateUi(self, Subcategory):
        _translate = QtCore.QCoreApplication.translate
        Subcategory.setWindowTitle(_translate("Subcategory", "Dialog"))
        self.lbl_title.setText(_translate("Subcategory", "Subcategory"))
        self.lbl_name.setText(_translate("Subcategory", "Subcategory name : "))
        self.label.setText(_translate("Subcategory", "Category : "))
        self.btn_cancel.setText(_translate("Subcategory", "Cancel"))
        self.btn_create.setText(_translate("Subcategory", "Create"))

