"""
This module contains the textedit subclasses used in LabNote software
"""

# Python import

# PyQt import
from PyQt5.QtWidgets import QTextEdit, QCompleter
from PyQt5.QtCore import Qt, QStringListModel, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor

# Project import
from labnote.resources import resources


class TextEdit(QTextEdit):
    """ This class is the base subclass of QTextEdit

    It handle tagging and plain text copy & pasting
    It does not handle drag and drop and complex operation.
    """

    # Global variable
    start_position = -1
    completer = None
    completer_status = False

    # Signals
    delete_tag = pyqtSignal(str)
    create_tag = pyqtSignal(str)

    def insertFromMimeData(self, source):
        """ Insert plain text only when pasting """
        self.insertPlainText(source.text())

    def keyPressEvent(self, event):
        """ Handle keypress event for the completer """
        is_tag = ((event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_T)
        ctrlOrShift = event.modifiers() == (Qt.ControlModifier or Qt.ShiftModifier)

        # Ignore keys that must be send to completer
        if self.completer:
            if self.completer.popup().isVisible():
                if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return or\
                        event.key() == Qt.Key_Escape or event.key() == Qt.Key_Tab or\
                        event.key() == Qt.Key_Backtab:
                    event.ignore()
                    return

        # Start the tag completer when the shortcut is pressed
        if is_tag:
            if not self.completer_status and self.textCursor().hasSelection():
                selection = self.textCursor().selection().toPlainText()
                if not self.has_space(selection) and not self.has_word_separator(selection):
                    self.format_completion(self.textCursor().selectionStart(), self.textCursor().selectionEnd())
                    return
            elif not self.completer_status:
                self.start_completer()
            else:
                return

        # Handle delete when the tag completer is active
        if event.key() == Qt.Key_Backspace and self.completer_status:
            if self.textCursor().hasSelection():
                QTextEdit.keyPressEvent(self, event)
                self.stop_completer()
                return
            else:
                current_position = self.textCursor().position()
                cursor = self.textCursor()
                cursor.setPosition(self.start_position)
                cursor.setPosition(current_position, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
                self.completer.popup().hide()
                return

        # Handle delete a tag when the completer is inactive
        if event.key() == Qt.Key_Backspace and not self.completer_status:
            if self.textCursor().charFormat().isAnchor():
                if self.textCursor().hasSelection():
                    self.delete_tag.emit(self.textCursor().charFormat().anchorHref())
                    QTextEdit.keyPressEvent(self, event)
                    return
                else:
                    self.select_anchor()
                    return

        # Stop if the return modifier is pressed with the completer open
        if self.completer_status and (ctrlOrShift or not event.text()):
            return

        # Add the tag if space is pressed
        if self.completer_status and event.text():
            char = event.text()[0]
            if self.is_space(char):
                self.format_completion()
                self.stop_completer()
                return

        # Handle all other key events normally
        QTextEdit.keyPressEvent(self, event)

        # Stop if the tag completer is not active
        if not self.completer_status:
            return

        # Stop the completer on end of word
        if event.text():
            char = event.text()[0]
            if self.is_word_separator(char):
                self.stop_completer()

        # Show the tag completer
        completion_prefix = self.text_under_cursor()

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        rect = self.cursorRect()
        rect.setWidth(self.completer.popup().sizeHintForColumn(0) +
                      self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(rect)

    def start_completer(self):
        completer = QCompleter()
        completer.setModel(QStringListModel(['tag_1', 'tag_2', 'tag_3']))
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setWrapAround(False)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.set_completer(completer)
        self.completer_status = True
        self.start_position = self.textCursor().position()

    def stop_completer(self):
        self.completer.setWidget(None)
        self.completer_status = False
        self.start_position = -1

    def text_under_cursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    def set_completer(self, completer):
        """ Set the completer to the textedit """
        self.completer = completer
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        """ Insert the completed word """
        extra = len(completion) - len(self.completer.completionPrefix())
        self.textCursor().insertText(completion[-extra:])
        self.format_completion()

    def format_completion(self, *args):
        """ Format the completed text

        :param args: Cursor start and end position
        :type args: int
        """

        # Set tag format
        format = QTextCharFormat()
        format.setBackground(QColor(212, 212, 212, 150))
        format.setAnchor(True)

        # Set format in text
        cursor = self.textCursor()
        if len(args) == 0:
            # Replace current text
            current_position = cursor.position()
            cursor.setPosition(self.start_position)
            cursor.setPosition(current_position, QTextCursor.KeepAnchor)
            old_text = cursor.selection().toPlainText()
            cursor.removeSelectedText()

            new_text = old_text.replace('_', ' ')
            self.textCursor().insertText(new_text)
            self.textCursor().insertText(" ")

            cursor.setPosition(self.start_position)
            cursor.setPosition(current_position, QTextCursor.KeepAnchor)
            format.setAnchorHref("tag/{}".format(old_text))
            cursor.mergeCharFormat(format)

            self.stop_completer()
            self.create_tag.emit(old_text)
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            cursor.setPosition(args[0])
            cursor.setPosition(args[1], QTextCursor.KeepAnchor)
            old_text = cursor.selection().toPlainText()
            cursor.removeSelectedText()

            new_text = old_text.replace('_', ' ')
            self.textCursor().insertText(new_text)
            self.textCursor().insertText(" ")

            cursor.setPosition(args[0])
            cursor.setPosition(args[1], QTextCursor.KeepAnchor)
            format.setAnchorHref("tag/{}".format(old_text))
            cursor.mergeCharFormat(format)
            self.create_tag.emit(old_text)

    def select_anchor(self):
        """ Select an anchor in the textedit """
        cursor = self.textCursor()

        current_position = self.textCursor().position()
        start = current_position
        end = current_position

        anchor = True
        while cursor.movePosition(QTextCursor.PreviousCharacter) and anchor:
            if not cursor.charFormat().isAnchor():
                start = cursor.position()
                anchor = False
            if cursor.position() == 0:
                start = cursor.position()

        while cursor.movePosition(QTextCursor.NextCharacter) and anchor:
            if not cursor.charFormat().isAnchor():
                end = cursor.position()
                anchor = False

        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def is_word_separator(self, char):
        """ Indicate if the caracter is a word separator

        :param char: Caracter to check
        :type char: str
        :return: True if it is a word separator
        """
        if char in "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-=":
            return True
        else:
            return False

    def is_space(self, char):
        """ Return if the caracter is a space

        :param char: Caracter to check
        :type char: str
        :return: True if it is a word separator
        """
        if char == " ":
            return True
        else:
            return False

    def has_word_separator(self, string):
        """ Return if a string contains a word separator

        :param string: String to check
        :type string: str
        :return: True if the string contains a word separator
        """

        for char in string:
            if char in "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-=":
                return True

        return False

    def has_space(self, string):
        """ Return if a string contains a space

        :param string: String to check
        :type string: str
        :return: True if the string contains a space
        """
        if " " in string:
            return True
        else:
            return False