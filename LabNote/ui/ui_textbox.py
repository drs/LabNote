# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/samueldrouin/SDR Soft/LabNote/LabNote/ui/qt_ui/textbox.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TextBox(object):
    def setupUi(self, TextBox):
        TextBox.setObjectName("TextBox")
        TextBox.resize(662, 462)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(TextBox)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame = QtWidgets.QFrame(TextBox)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.icon_frame = QtWidgets.QFrame(self.frame)
        self.icon_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.icon_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.icon_frame.setObjectName("icon_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.icon_frame)
        self.horizontalLayout.setContentsMargins(-1, 6, 12, 6)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_style = QtWidgets.QPushButton(self.icon_frame)
        self.btn_style.setObjectName("btn_style")
        self.horizontalLayout.addWidget(self.btn_style)
        self.widget = QtWidgets.QWidget(self.icon_frame)
        self.widget.setMinimumSize(QtCore.QSize(10, 0))
        self.widget.setMaximumSize(QtCore.QSize(10, 16777215))
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.btn_bold = QtWidgets.QPushButton(self.icon_frame)
        self.btn_bold.setCheckable(True)
        self.btn_bold.setObjectName("btn_bold")
        self.horizontalLayout.addWidget(self.btn_bold)
        self.btn_italic = QtWidgets.QPushButton(self.icon_frame)
        self.btn_italic.setCheckable(True)
        self.btn_italic.setObjectName("btn_italic")
        self.horizontalLayout.addWidget(self.btn_italic)
        self.btn_underline = QtWidgets.QPushButton(self.icon_frame)
        self.btn_underline.setCheckable(True)
        self.btn_underline.setObjectName("btn_underline")
        self.horizontalLayout.addWidget(self.btn_underline)
        self.btn_strikethrough = QtWidgets.QPushButton(self.icon_frame)
        self.btn_strikethrough.setCheckable(True)
        self.btn_strikethrough.setObjectName("btn_strikethrough")
        self.horizontalLayout.addWidget(self.btn_strikethrough)
        self.widget_3 = QtWidgets.QWidget(self.icon_frame)
        self.widget_3.setMinimumSize(QtCore.QSize(10, 0))
        self.widget_3.setMaximumSize(QtCore.QSize(10, 16777215))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout.addWidget(self.widget_3)
        self.btn_superscript = QtWidgets.QPushButton(self.icon_frame)
        self.btn_superscript.setText("")
        self.btn_superscript.setCheckable(True)
        self.btn_superscript.setObjectName("btn_superscript")
        self.horizontalLayout.addWidget(self.btn_superscript)
        self.btn_subscript = QtWidgets.QPushButton(self.icon_frame)
        self.btn_subscript.setText("")
        self.btn_subscript.setCheckable(True)
        self.btn_subscript.setObjectName("btn_subscript")
        self.horizontalLayout.addWidget(self.btn_subscript)
        self.widget_2 = QtWidgets.QWidget(self.icon_frame)
        self.widget_2.setMinimumSize(QtCore.QSize(10, 0))
        self.widget_2.setMaximumSize(QtCore.QSize(10, 16777215))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout.addWidget(self.widget_2)
        self.btn_color = QtWidgets.QPushButton(self.icon_frame)
        self.btn_color.setText("")
        self.btn_color.setObjectName("btn_color")
        self.horizontalLayout.addWidget(self.btn_color)
        self.btn_highlight = QtWidgets.QPushButton(self.icon_frame)
        self.btn_highlight.setText("")
        self.btn_highlight.setObjectName("btn_highlight")
        self.horizontalLayout.addWidget(self.btn_highlight)
        self.btn_list = QtWidgets.QPushButton(self.icon_frame)
        self.btn_list.setText("")
        self.btn_list.setCheckable(True)
        self.btn_list.setObjectName("btn_list")
        self.horizontalLayout.addWidget(self.btn_list)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.icon_frame)
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(TextBox)
        QtCore.QMetaObject.connectSlotsByName(TextBox)

    def retranslateUi(self, TextBox):
        _translate = QtCore.QCoreApplication.translate
        TextBox.setWindowTitle(_translate("TextBox", "Form"))
        self.btn_style.setToolTip(_translate("TextBox", "Text format"))
        self.btn_style.setText(_translate("TextBox", "§"))
        self.btn_bold.setToolTip(_translate("TextBox", "Bold"))
        self.btn_bold.setText(_translate("TextBox", "B"))
        self.btn_italic.setToolTip(_translate("TextBox", "Italic"))
        self.btn_italic.setText(_translate("TextBox", "I"))
        self.btn_underline.setToolTip(_translate("TextBox", "Underline"))
        self.btn_underline.setText(_translate("TextBox", "U"))
        self.btn_strikethrough.setToolTip(_translate("TextBox", "Strikethrough"))
        self.btn_strikethrough.setText(_translate("TextBox", "abc"))
        self.btn_superscript.setToolTip(_translate("TextBox", "Superscript"))
        self.btn_subscript.setToolTip(_translate("TextBox", "Subscript"))
        self.btn_color.setToolTip(_translate("TextBox", "Text color"))
        self.btn_highlight.setToolTip(_translate("TextBox", "Highlight color"))
        self.btn_list.setToolTip(_translate("TextBox", "List type"))
