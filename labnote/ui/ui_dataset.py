# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/Development/LabNote/labnote/ui/qt_ui/dataset.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dataset(object):
    def setupUi(self, Dataset):
        Dataset.setObjectName("Dataset")
        Dataset.resize(751, 490)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dataset)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(Dataset)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.layout_search = QtWidgets.QHBoxLayout()
        self.layout_search.setSpacing(0)
        self.layout_search.setObjectName("layout_search")
        self.btn_import = QtWidgets.QToolButton(Dataset)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_import.sizePolicy().hasHeightForWidth())
        self.btn_import.setSizePolicy(sizePolicy)
        self.btn_import.setMinimumSize(QtCore.QSize(0, 0))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(191, 191, 191))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(168, 168, 168))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 212, 212))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(191, 191, 191))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(169, 169, 169))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 212, 212))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(191, 191, 191))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(169, 169, 169))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 212, 212))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        self.btn_import.setPalette(palette)
        self.btn_import.setText("")
        self.btn_import.setObjectName("btn_import")
        self.layout_search.addWidget(self.btn_import)
        spacerItem = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem)
        self.line = QtWidgets.QFrame(Dataset)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.layout_search.addWidget(self.line)
        spacerItem1 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem1)
        self.btn_r = QtWidgets.QToolButton(Dataset)
        self.btn_r.setText("")
        self.btn_r.setObjectName("btn_r")
        self.layout_search.addWidget(self.btn_r)
        spacerItem2 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem2)
        self.btn_r_run = QtWidgets.QToolButton(Dataset)
        self.btn_r_run.setText("")
        self.btn_r_run.setObjectName("btn_r_run")
        self.layout_search.addWidget(self.btn_r_run)
        spacerItem3 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem3)
        self.line_2 = QtWidgets.QFrame(Dataset)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.layout_search.addWidget(self.line_2)
        spacerItem4 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem4)
        self.btn_python = QtWidgets.QToolButton(Dataset)
        self.btn_python.setText("")
        self.btn_python.setObjectName("btn_python")
        self.layout_search.addWidget(self.btn_python)
        spacerItem5 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem5)
        self.btn_python_run = QtWidgets.QToolButton(Dataset)
        self.btn_python_run.setText("")
        self.btn_python_run.setObjectName("btn_python_run")
        self.layout_search.addWidget(self.btn_python_run)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_search.addItem(spacerItem6)
        self.verticalLayout_3.addLayout(self.layout_search)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.frame = QtWidgets.QFrame(Dataset)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_tree = QtWidgets.QFrame(self.frame)
        self.frame_tree.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_tree.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_tree.setObjectName("frame_tree")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_tree)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_add = QtWidgets.QPushButton(self.frame_tree)
        self.btn_add.setAutoDefault(False)
        self.btn_add.setFlat(True)
        self.btn_add.setObjectName("btn_add")
        self.horizontalLayout.addWidget(self.btn_add)
        self.btn_manage = QtWidgets.QPushButton(self.frame_tree)
        self.btn_manage.setText("")
        self.btn_manage.setAutoDefault(False)
        self.btn_manage.setFlat(True)
        self.btn_manage.setObjectName("btn_manage")
        self.horizontalLayout.addWidget(self.btn_manage)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem7)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addWidget(self.frame_tree)
        self.layout_entry = QtWidgets.QHBoxLayout()
        self.layout_entry.setSpacing(0)
        self.layout_entry.setObjectName("layout_entry")
        self.widget = QtWidgets.QWidget(self.frame)
        self.widget.setObjectName("widget")
        self.layout_entry.addWidget(self.widget)
        self.horizontalLayout_3.addLayout(self.layout_entry)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 10)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(12, 6, 12, 12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem8)
        self.btn_close = QtWidgets.QPushButton(Dataset)
        self.btn_close.setAutoDefault(False)
        self.btn_close.setObjectName("btn_close")
        self.horizontalLayout_2.addWidget(self.btn_close)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dataset)
        QtCore.QMetaObject.connectSlotsByName(Dataset)

    def retranslateUi(self, Dataset):
        _translate = QtCore.QCoreApplication.translate
        Dataset.setWindowTitle(_translate("Dataset", "Dialog"))
        self.label.setText(_translate("Dataset", "Dataset"))
        self.btn_add.setText(_translate("Dataset", "+"))
        self.btn_close.setText(_translate("Dataset", "Close"))

