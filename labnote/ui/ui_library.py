# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/library.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Library(object):
    def setupUi(self, Library):
        Library.setObjectName("Library")
        Library.resize(700, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Library.sizePolicy().hasHeightForWidth())
        Library.setSizePolicy(sizePolicy)
        Library.setMinimumSize(QtCore.QSize(700, 400))
        Library.setSizeGripEnabled(True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Library)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.layout_title = QtWidgets.QHBoxLayout()
        self.layout_title.setContentsMargins(12, 10, 12, 6)
        self.layout_title.setObjectName("layout_title")
        self.label_2 = QtWidgets.QLabel(Library)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.layout_title.addWidget(self.label_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_title.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.layout_title)
        self.main_frame = QtWidgets.QFrame(Library)
        self.main_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frame.setObjectName("main_frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.main_frame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.detail_layout = QtWidgets.QVBoxLayout()
        self.detail_layout.setContentsMargins(12, 6, 0, 0)
        self.detail_layout.setObjectName("detail_layout")
        self.layout_form = QtWidgets.QFormLayout()
        self.layout_form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.layout_form.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.layout_form.setContentsMargins(-1, -1, 7, -1)
        self.layout_form.setVerticalSpacing(0)
        self.layout_form.setObjectName("layout_form")
        self.lbl_key = QtWidgets.QLabel(self.main_frame)
        self.lbl_key.setMinimumSize(QtCore.QSize(120, 0))
        self.lbl_key.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_key.setFont(font)
        self.lbl_key.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbl_key.setObjectName("lbl_key")
        self.layout_form.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_key)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_5.setContentsMargins(-1, -1, 12, 0)
        self.horizontalLayout_5.setSpacing(10)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.txt_key = QtWidgets.QLineEdit(self.main_frame)
        self.txt_key.setPlaceholderText("")
        self.txt_key.setObjectName("txt_key")
        self.horizontalLayout_5.addWidget(self.txt_key)
        self.comboBox = QtWidgets.QComboBox(self.main_frame)
        self.comboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.comboBox.setMaximumSize(QtCore.QSize(150, 16777215))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_5.addWidget(self.comboBox)
        self.layout_form.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_5)
        self.detail_layout.addLayout(self.layout_form)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btn_save = QtWidgets.QPushButton(self.main_frame)
        self.btn_save.setAutoDefault(False)
        self.btn_save.setObjectName("btn_save")
        self.horizontalLayout_2.addWidget(self.btn_save)
        self.detail_layout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4.addLayout(self.detail_layout)
        self.verticalLayout_2.addWidget(self.main_frame)

        self.retranslateUi(Library)
        QtCore.QMetaObject.connectSlotsByName(Library)
        Library.setTabOrder(self.txt_key, self.comboBox)
        Library.setTabOrder(self.comboBox, self.btn_save)

    def retranslateUi(self, Library):
        _translate = QtCore.QCoreApplication.translate
        Library.setWindowTitle(_translate("Library", "Dialog"))
        self.label_2.setText(_translate("Library", "Library"))
        self.lbl_key.setText(_translate("Library", "Key "))
        self.comboBox.setItemText(0, _translate("Library", "Article"))
        self.comboBox.setItemText(1, _translate("Library", "Book"))
        self.comboBox.setItemText(2, _translate("Library", "Chapter"))
        self.comboBox.setItemText(3, _translate("Library", "Thesis"))
        self.btn_save.setText(_translate("Library", "Save"))

