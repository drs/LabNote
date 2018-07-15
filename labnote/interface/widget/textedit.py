"""
This module contains the textedit subclasses used in LabNote software
"""

# Python import

# PyQt import
from PyQt5.QtWidgets import QTextEdit, QCompleter, QPlainTextEdit
from PyQt5.QtCore import Qt, QStringListModel, QUrl, QFileInfo
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QImage, QImageReader, QTextBlock

# Project import
from labnote.utils import files
from labnote.core import common


class PlainTextEdit(QPlainTextEdit):
    def __init__(self):
        super(PlainTextEdit, self).__init__()
        self.setStyleSheet("QPlainTextEdit:disabled { background-color: white } ")

    def insertFromMimeData(self, source):
        """ Insert plain text only when pasting """
        self.insertPlainText(source.text())


class TextEdit(QTextEdit):
    """ Base subclass of all the other text edit """
    def __init__(self):
        super(TextEdit, self).__init__()
        self.setStyleSheet("QTextEdit:disabled { background-color: white } ")

    def insertFromMimeData(self, source):
        """ Insert plain text only when pasting """
        self.insertPlainText(source.text())


TAG_COMPLETER = 20
REFERENCE_COMPLETER = 21
PROTOCOL_COMPLETER = 22
DATASET_COMPLETER = 23


class CompleterTextEdit(TextEdit):
    """ This class is the base subclass of QTextEdit

    It handle tagging and plain text copy & pasting
    It does not handle drag and drop and complex operation.
    """

    # Global variable
    launch = True  # Changed to false when the text is first formatted
    start_position = -1
    completer = None
    completer_status = False
    completer_type = -1
    accept_tag = False
    accept_reference = False
    accept_dataset = False
    accept_protocol = False

    def __init__(self, tag_list=None, reference_list=None, dataset_list=None, protocol_list=None):
        super(CompleterTextEdit, self).__init__()
        if tag_list is not None:
            self.tag_list = set(tag_list)
            self.accept_tag = True

        if reference_list is not None:
            self.reference_list = set(reference_list)
            self.accept_reference = True

        if dataset_list is not None:
            self.dataset_list = set(dataset_list)
            self.accept_dataset = True

        if protocol_list is not None:
            self.protocol_list = set(protocol_list)
            self.accept_protocol = True

        self.textChanged.connect(self.set_base_format)

    def set_base_format(self):
        """ Set the TextEdit base format """
        self.blockSignals(True)

        cursor = self.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)

        # Set the initial format
        #if self.launch:
            #fmt = QTextCharFormat()
            #fmt.setFontUnderline(False)
            #fmt.setForeground(Qt.black)

            #cursor.mergeCharFormat(fmt)
            #self.launch = False

        self.blockSignals(False)
        self.textChanged.disconnect(self.set_base_format)

    def keyPressEvent(self, event):
        """ Handle keypress event for the completer """
        is_tag = ((event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_T)
        is_reference = ((event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_R)
        is_dataset = ((event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_D)
        is_protocol = ((event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_P)
        ctrlOrShift = event.modifiers() == (Qt.ControlModifier or Qt.ShiftModifier)

        # Start the tag completer when the shortcut is pressed
        if self.accept_tag and is_tag:
            if not self.completer_status and self.textCursor().hasSelection():
                selection = self.textCursor().selection().toPlainText()
                if not self.has_space(selection) and not self.has_word_separator(selection):
                    self.format_completion(self.textCursor().selectionStart(),
                                           self.textCursor().selectionEnd(),
                                           TAG_COMPLETER)
                    return
            elif not self.completer_status:
                self.start_completer(self.tag_list, TAG_COMPLETER)
            else:
                return

        if self.accept_reference and is_reference:
            if not self.completer_status:
                self.start_completer(self.reference_list, REFERENCE_COMPLETER)
            else:
                return

        if self.accept_dataset and is_dataset:
            if not self.completer_status:
                self.start_completer(self.dataset_list, DATASET_COMPLETER)
            else:
                return

        if self.accept_protocol and is_protocol:
            if not self.completer_status:
                self.start_completer(self.protocol_list, PROTOCOL_COMPLETER)
            else:
                return

        # Handle delete a tag when the completer is inactive
        if event.key() == Qt.Key_Backspace and not self.completer_status:
            cursor = self.textCursor()
            if cursor.hasSelection():
                start = cursor.selectionStart()
                old_start = start
                end = cursor.selectionEnd()
                old_end = end

                cursor.setPosition(start)
                anchor_begin = cursor.charFormat().isAnchor()
                cursor.setPosition(start)
                anchor_end = cursor.charFormat().isAnchor()

                cursor.setPosition(start)
                while cursor.movePosition(QTextCursor.PreviousCharacter) and anchor_begin:
                    if not cursor.charFormat().isAnchor():
                        start = cursor.position()
                        anchor_begin = False
                    if cursor.position() == 0:
                        start = cursor.position()

                cursor.setPosition(end)
                while cursor.movePosition(QTextCursor.NextCharacter) and anchor_end:
                    if not cursor.charFormat().isAnchor():
                        end = cursor.position()
                        anchor_end = False

                if start != old_start or end != old_end:
                    cursor.setPosition(start)
                    cursor.setPosition(end, QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)
                else:
                    QTextEdit.keyPressEvent(self, event)
                return
            else:
                if self.textCursor().charFormat().isAnchor():
                    self.select_anchor()
                    return

        # Remove the anchor format for the text added directory after an anchor
        if event.text() and self.textCursor().charFormat().isAnchor() and not self.textCursor().hasSelection():

            cursor = self.textCursor()
            old_position = cursor.position()
            QTextEdit.keyPressEvent(self, event)
            new_position = cursor.position()
            cursor.setPosition(old_position)
            cursor.setPosition(new_position, QTextCursor.KeepAnchor)
            fmt = cursor.charFormat()
            fmt.setAnchor(False)
            if cursor.charFormat().anchorHref().split('/')[0] == 'tag':
                fmt.setBackground(Qt.white)
            cursor.mergeCharFormat(fmt)
            return

        # Stop if the completer is not active
        if not self.completer_status:
            QTextEdit.keyPressEvent(self, event)
            return

        # Stop on control or shift or if the event does not contain text
        if ctrlOrShift or not event.text():
            if self.completer_status and self.textCursor().hasSelection() and event.key() == Qt.Key_Right:
                QTextEdit.keyPressEvent(self, event)
            return

        # Ignore keys that must be send to completer
        if self.completer.popup().isVisible():
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return or \
                    event.key() == Qt.Key_Escape or event.key() == Qt.Key_Tab or \
                    event.key() == Qt.Key_Backtab:
                event.ignore()
                return

        # Handle delete when the tag completer is active
        if event.key() == Qt.Key_Backspace:
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

        # Add the tag when the end of the word is reached
        if self.is_space(event.text()[0]) or self.is_word_separator(event.text()[0]) or \
                event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return or \
                event.key() == Qt.Key_Escape or event.key() == Qt.Key_Tab or \
                event.key() == Qt.Key_Backtab:
            if self.completer_type == TAG_COMPLETER:
                self.format_completion()
            else:
                QTextEdit.keyPressEvent(self, event)
            self.stop_completer()
            return

        # Handle all other key events normally
        QTextEdit.keyPressEvent(self, event)

        # Show the tag completer
        completion_prefix = self.text_under_cursor()

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        rect = self.cursorRect()
        rect.setWidth(self.completer.popup().sizeHintForColumn(0) +
                        self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(rect)

    def anchors(self):
        """ Return all the anchors in the current document """
        cursor = self.textCursor()
        cursor.setPosition(0)

        tag_list = set([])
        reference_list = set([])
        dataset_list = set([])
        protocol_list = set([])

        while cursor.movePosition(QTextCursor.NextCharacter):
            if cursor.charFormat().isAnchor():
                href = cursor.charFormat().anchorHref().split('/')
                prefix = href[0]
                value = href[1]

                if prefix == 'tag':
                    tag_list.add(value)
                elif prefix == 'reference':
                    reference_list.add(value)
                elif prefix == 'dataset':
                    dataset_list.add(value)
                elif prefix == 'protocol':
                    protocol_list.add(value)

        anchor = {}
        if self.accept_tag:
            anchor['tag'] = list(tag_list)
        if self.accept_reference:
            anchor['reference'] = list(reference_list)
        if self.accept_dataset:
            anchor['dataset'] = list(dataset_list)
        if self.accept_protocol:
            anchor['protocol'] = list(protocol_list)

        return anchor

    def format_completion(self, *args):
        """ Format the completed text

        :param args: Cursor start and end position
        :type args: int
        """
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

            # Set the format
            fmt = cursor.charFormat()
            if self.completer_type == TAG_COMPLETER:
                fmt.setBackground(QColor(212, 212, 212, 150))
            fmt.setAnchor(True)

            if self.completer_type == TAG_COMPLETER:
                fmt.setAnchorHref("tag/{}".format(old_text))
            elif self.completer_type == REFERENCE_COMPLETER:
                fmt.setAnchorHref("reference/{}".format(old_text))
            elif self.completer_type == DATASET_COMPLETER:
                fmt.setAnchorHref("dataset/{}".format(old_text))
            elif self.completer_type == PROTOCOL_COMPLETER:
                fmt.setAnchorHref("protocol/{}".format(old_text))
            cursor.mergeCharFormat(fmt)
            self.stop_completer()
        elif len(args) == 3 and \
                isinstance(args[0], int) and \
                isinstance(args[1], int) and \
                isinstance(args[2], int):
            cursor.setPosition(args[0])
            cursor.setPosition(args[1], QTextCursor.KeepAnchor)
            old_text = cursor.selection().toPlainText()
            cursor.removeSelectedText()

            new_text = old_text.replace('_', ' ')
            self.textCursor().insertText(new_text)
            self.textCursor().insertText(" ")

            cursor.setPosition(args[0])
            cursor.setPosition(args[1], QTextCursor.KeepAnchor)

            # Set the format
            fmt = cursor.charFormat()
            if self.completer_type == TAG_COMPLETER:
                fmt.setBackground(QColor(212, 212, 212, 150))
            fmt.setAnchor(True)

            if args[2] == TAG_COMPLETER:
                fmt.setAnchorHref("tag/{}".format(old_text))
            cursor.mergeCharFormat(fmt)

    def start_completer(self, completer_list, completer_type):
        completer = QCompleter()
        completer.setModel(QStringListModel(list(completer_list)))
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setWrapAround(False)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.set_completer(completer)
        self.completer_status = True
        self.completer_type = completer_type
        self.start_position = self.textCursor().position()

    def stop_completer(self):
        self.completer.setWidget(None)
        self.completer_status = False
        self.completer_type = -1
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
        if char in "~!@#$%^&*()+{}|:\"<>?,./;'[]\\=":
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
            if char in "~!@#$%^&*()+{}|:\"<>?,./;'[]\\=":
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


class ImageTextEdit(CompleterTextEdit):
    """ Completer text edit subclass that handle image drag and drop and copy paste """

    # Class variable definition
    accept_image = False
    uuid = None
    deleted_image = set([])

    def __init__(self, editor_type, reference_list=None, dataset_list=None, protocol_list=None):
        super(ImageTextEdit, self).__init__(reference_list=reference_list,
                                            dataset_list=dataset_list, protocol_list=protocol_list)
        self.editor_type = editor_type

    def set_uuid(self, uuid):
        self.accept_image = True
        self.uuid = uuid

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()

                cursor.setPosition(start)
                while cursor.movePosition(QTextCursor.NextCharacter) and cursor.position() <= end:
                    if cursor.charFormat().isImageFormat():
                        self.deleted_image.add(cursor.charFormat().toImageFormat().name())
            else:
                if cursor.charFormat().isImageFormat():
                    self.deleted_image.add(cursor.charFormat().toImageFormat().name())

        super(ImageTextEdit, self).keyPressEvent(event)

    def is_image(self):
        if self.textCursor().charFormat().isImageFormat():
            return True
        return False

    def canInsertFromMimeData(self, source):
        """ Reimplanted QTextBrowser function

        This function check if the source has image or urls

        :param source: Source data
        :type source: QMimeData
        :returns: If source has image, url or can be inserted from mime data
        """
        if self.accept_image:
            if source.hasUrls():
                return source.hasUrls()
            return QTextEdit().canInsertFromMimeData(source)
        else:
            return False

    def insertFromMimeData(self, source):
        """ Insert source from mime data in the text browser

        :param source: Source data
        :type source: QMimeData
        """
        if source.hasUrls():
            for url in source.urls():
                info = QFileInfo(url.toLocalFile())
                if info.suffix().lower().encode('latin-1') in QImageReader.supportedImageFormats():
                    self.insert_image(url)
        else:
            self.insertPlainText(source.text())

    def insert_image(self, url):
        """ Insert image in the document

        :param url: File url
        :type url: QUrl
        """
        path = None
        if url:
            if self.editor_type == common.TYPE_PROTOCOL:
                path = files.add_image_protocol(self.uuid, url.toLocalFile(), QFileInfo(url.toLocalFile()).suffix())

        if path:
            image = QImage(path)
            if image:
                self.textCursor().insertImage(path)

                cursor = self.textCursor()
                cursor.setPosition(self.textCursor().position()-1)
                cursor.setPosition(self.textCursor().position(), QTextCursor.KeepAnchor)
                fmt = cursor.charFormat().toImageFormat()
                fmt.setWidth(image.width())
                fmt.setHeight(image.height())
                cursor.setCharFormat(fmt)
                self.setTextCursor(cursor)
