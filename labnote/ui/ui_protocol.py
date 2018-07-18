# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/protocol.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Protocol(object):
    def setupUi(self, Protocol):
        Protocol.setObjectName("Protocol")
        Protocol.resize(719, 473)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Protocol)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Protocol)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.layout_search = QtWidgets.QHBoxLayout()
        self.layout_search.setSpacing(0)
        self.layout_search.setObjectName("layout_search")
        self.btn_export = QtWidgets.QToolButton(Protocol)
        self.btn_export.setText("")
        self.btn_export.setObjectName("btn_export")
        self.layout_search.addWidget(self.btn_export)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem)
        self.verticalLayout.addLayout(self.layout_search)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.frame = QtWidgets.QFrame(Protocol)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.layout_entry = QtWidgets.QVBoxLayout()
        self.layout_entry.setObjectName("layout_entry")
        self.horizontalLayout_4.addLayout(self.layout_entry)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btn_close = QtWidgets.QPushButton(Protocol)
        self.btn_close.setAutoDefault(False)
        self.btn_close.setObjectName("btn_close")
        self.horizontalLayout_2.addWidget(self.btn_close)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Protocol)
        QtCore.QMetaObject.connectSlotsByName(Protocol)

    def retranslateUi(self, Protocol):
        _translate = QtCore.QCoreApplication.translate
        Protocol.setWindowTitle(_translate("Protocol", "Dialog"))
        self.label.setText(_translate("Protocol", "Protocol"))
        self.btn_close.setText(_translate("Protocol", "Close"))

