# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/sample.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Sample(object):
    def setupUi(self, Sample):
        Sample.setObjectName("Sample")
        Sample.resize(698, 461)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Sample)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.layout_title = QtWidgets.QHBoxLayout()
        self.layout_title.setContentsMargins(6, 6, 6, 6)
        self.layout_title.setObjectName("layout_title")
        self.label = QtWidgets.QLabel(Sample)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.layout_title.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_title.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.layout_title)
        self.frame = QtWidgets.QFrame(Sample)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table = QtWidgets.QTableWidget(self.frame)
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.verticalLayout.addWidget(self.table)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(12, 6, 12, 12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btn_close = QtWidgets.QPushButton(self.frame)
        self.btn_close.setAutoDefault(False)
        self.btn_close.setObjectName("btn_close")
        self.horizontalLayout_2.addWidget(self.btn_close)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.frame)

        self.retranslateUi(Sample)
        QtCore.QMetaObject.connectSlotsByName(Sample)

    def retranslateUi(self, Sample):
        _translate = QtCore.QCoreApplication.translate
        Sample.setWindowTitle(_translate("Sample", "Dialog"))
        self.label.setText(_translate("Sample", "Sample Number"))
        self.btn_close.setText(_translate("Sample", "Close"))

