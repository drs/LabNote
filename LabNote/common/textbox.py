from PyQt5.QtWidgets import QWidget, QMenu, QAction
from PyQt5.QtGui import QTextCharFormat, QFont, QTextDocument, QPixmap, QPainter, QIcon
from PyQt5.QtCore import Qt, QRectF

from ui.ui_textbox import Ui_TextBox
from common import style


class Textbox(QWidget, Ui_TextBox):
    """
    Textbox widget class

    The textbox widget is a mini text editor that is used to edit protocols and experiments
    """
    def __init__(self):
        super(Textbox, self).__init__()
        self.setupUi(self)

        # Set button groups
        self.btn_bold.setProperty("Menu", False)
        self.btn_italic.setProperty("Menu", False)
        self.btn_underline.setProperty("Menu", False)
        self.btn_strikethrough.setProperty("Menu", False)
        self.btn_superscript.setProperty("Menu", False)
        self.btn_subscript.setProperty("Menu", False)
        self.btn_style.setProperty("Menu", True)
        self.btn_color.setProperty("Menu", True)
        self.btn_highlight.setProperty("Menu", True)
        self.btn_list.setProperty("Menu", True)

        # Style menu
        self.act_part = QAction("Part", self)
        self.act_part.triggered.connect(self.format_part)
        self.act_part.setProperty("Level", 0)
        self.act_section = QAction("Section", self)
        self.act_section.triggered.connect(self.format_section)
        self.act_section.setProperty("Level", 1)
        self.act_subsection = QAction("Subsection", self)
        self.act_subsection.triggered.connect(self.format_subsection)
        self.act_subsection.setProperty("Level", 2)
        self.act_subsubsection = QAction("Subsubsection", self)
        self.act_subsubsection.triggered.connect(self.format_subsubsection)
        self.act_subsubsection.setProperty("Level", 3)
        self.act_body = QAction("Body", self)
        self.act_body.triggered.connect(self.format_body)
        self.act_body.setProperty("Level", 4)
        self.act_note = QAction("Note", self)
        self.act_note.triggered.connect(self.format_note)
        self.act_note.setProperty("Level", 5)

        self.style_menu = QMenu()
        self.style_menu.addAction(self.act_part)
        self.style_menu.addAction(self.act_section)
        self.style_menu.addAction(self.act_subsection)
        self.style_menu.addAction(self.act_subsubsection)
        self.style_menu.addAction(self.act_body)
        self.style_menu.addAction(self.act_note)
        self.btn_style.setMenu(self.style_menu)

        # Highlight color menu
        self.act_clear_highlight = QAction("Clear", self)
        self.act_clear_highlight.triggered.connect(self.format_clear_highlight)
        self.act_red_highlight = QAction("Red", self)
        self.act_red_highlight.triggered.connect(self.format_red_highlight)
        self.act_orange_highlight = QAction("Orange", self)
        self.act_orange_highlight.triggered.connect(self.format_organge_highlight)
        self.act_yellow_highlight = QAction("Yellow", self)
        self.act_yellow_highlight.triggered.connect(self.format_yellow_highlight)
        self.act_green_highlight = QAction("Green", self)
        self.act_green_highlight.triggered.connect(self.format_green_highlight)
        self.act_blue_highlight = QAction("Blue", self)
        self.act_blue_highlight.triggered.connect(self.format_blue_highlight)
        self.act_purple_highlight = QAction("Purple", self)
        self.act_purple_highlight.triggered.connect(self.format_purple_highlight)
        self.act_gray_highlight = QAction("Gray", self)
        self.act_gray_highlight.triggered.connect(self.format_gray_highlight)

        self.highlight_menu = QMenu()
        self.highlight_menu.addAction(self.act_clear_highlight)
        self.highlight_menu.addAction(self.act_yellow_highlight)
        self.highlight_menu.addAction(self.act_green_highlight)
        self.highlight_menu.addAction(self.act_blue_highlight)
        self.highlight_menu.addAction(self.act_red_highlight)
        self.highlight_menu.addAction(self.act_gray_highlight)
        self.btn_highlight.setMenu(self.highlight_menu)

        # Text color menu
        self.act_black_text = QAction("Black", self)
        self.act_black_text.triggered.connect(self.format_black_text)
        self.act_gray_text = QAction("Gray", self)
        self.act_gray_text.triggered.connect(self.format_gray_text)
        self.act_red_text = QAction("Red", self)
        self.act_red_text.triggered.connect(self.format_red_text)
        self.act_orange_text = QAction("Orange", self)
        self.act_orange_text.triggered.connect(self.format_orange_text)
        self.act_yellow_text = QAction("Yellow", self)
        self.act_yellow_text.triggered.connect(self.format_yellow_text)
        self.act_green_text = QAction("Green", self)
        self.act_green_text.triggered.connect(self.format_green_text)
        self.act_blue_text = QAction("Blue", self)
        self.act_blue_text.triggered.connect(self.format_blue_text)
        self.act_purple_text = QAction("Purple", self)
        self.act_purple_text.triggered.connect(self.format_purple_text)

        self.color_menu = QMenu()
        self.color_menu.addAction(self.act_black_text)
        self.color_menu.addAction(self.act_gray_text)
        self.color_menu.addAction(self.act_red_text)
        self.color_menu.addAction(self.act_orange_text)
        self.color_menu.addAction(self.act_yellow_text)
        self.color_menu.addAction(self.act_green_text)
        self.color_menu.addAction(self.act_blue_text)
        self.color_menu.addAction(self.act_purple_text)
        self.btn_color.setMenu(self.color_menu)

        # List menu
        self.act_no_list = QAction("No list", self)
        self.act_no_list.triggered.connect(self.format_no_list)
        self.act_bullet_list = QAction("Bullet", self)
        self.act_bullet_list.triggered.connect(self.format_bullet_list)
        self.act_dash_list = QAction("Dash", self)
        self.act_dash_list.triggered.connect(self.format_dash_list)
        self.act_numbered_list = QAction("Numbered", self)
        self.act_numbered_list.triggered.connect(self.format_numbered_list)
        self.act_roman_list = QAction("Roman numbered", self)
        self.act_roman_list.triggered.connect(self.format_roman_list)
        self.act_uppercase_list = QAction("Uppercase letters", self)
        self.act_uppercase_list.triggered.connect(self.format_uppercase_list)
        self.act_lowercase_list = QAction("Lowercase letters", self)
        self.act_lowercase_list.triggered.connect(self.format_lowercase_list)
        self.act_increase_indent = QAction("Increase indentation")
        self.act_increase_indent.triggered.connect(self.format_increase_indent)
        self.act_decrease_indent = QAction("Decrease indentation")
        self.act_decrease_indent.triggered.connect(self.format_decrease_indent)

        self.list_menu = QMenu()
        self.list_menu.addAction(self.act_no_list)
        self.list_menu.addAction(self.act_bullet_list)
        self.list_menu.addAction(self.act_dash_list)
        self.list_menu.addAction(self.act_numbered_list)
        self.list_menu.addAction(self.act_roman_list)
        self.list_menu.addAction(self.act_uppercase_list)
        self.list_menu.addAction(self.act_lowercase_list)
        self.list_menu.addSeparator()
        self.list_menu.addAction(self.act_increase_indent)
        self.list_menu.addAction(self.act_decrease_indent)

        self.btn_list.setMenu(self.list_menu)

        # Set style sheet
        style.set_style_sheet(self, ":/StyleSheet/style-sheet/textbox.qss")

        # Superscript button text
        text = QTextDocument()
        text.setHtml("<p style = color:#484848 >X<sup>&thinsp;2</sup></p>")

        pixmap = self.draw_icon(text)
        icon = QIcon(pixmap)
        self.btn_superscript.setIcon(icon)
        self.btn_superscript.setIconSize(pixmap.rect().size() / self.devicePixelRatioF())

        # Subscript button text
        text = QTextDocument()
        text.setHtml("<p style = color:#484848 >X<sub>&thinsp;2</sub></p>")

        pixmap = self.draw_icon(text)
        icon = QIcon(pixmap)
        self.btn_subscript.setIcon(icon)
        self.btn_subscript.setIconSize(pixmap.rect().size() / self.devicePixelRatioF())

        # Slots connection
        self.btn_bold.clicked.connect(self.format_bold)
        self.btn_italic.clicked.connect(self.format_italic)
        self.btn_underline.clicked.connect(self.format_underline)
        self.btn_strikethrough.clicked.connect(self.format_strikethrough)
        self.btn_superscript.clicked.connect(self.format_superscript)
        self.btn_subscript.clicked.connect(self.format_subscript)


    def draw_icon(self, text):
        """Draw an icon from a html text and return it as a pixmap.

        .. note::
            This function handle HiDPI as well a regular screen

        :param text: QTextDocument with HTML code for the icon.
        :type text: QTextDocument
        :returns:  QPixmap -- Icon pixmap

        """

        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(text.size().width() * dpr, text.size().height() * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        text.drawContents(painter, QRectF(pixmap.rect()))
        painter.end()

        return pixmap

    def merge_format_on_word_or_selection(self, fmt):
        """
        Change the caracter format when a format button is pressed.

        The font is changed for the selection or from the cursor position.
        :param fmt: Text format
        """
        cursor = self.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.textEdit.mergeCurrentCharFormat(fmt)

    def format_bold(self):
        """
        Set text format to bold.
        """
        fmt = QTextCharFormat()
        if self.btn_bold.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_italic(self):
        """
        Set text format to italic.
        """
        fmt = QTextCharFormat()
        if self.btn_italic.isChecked():
            fmt.setFontItalic(True)
        else:
            fmt.setFontItalic(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_underline(self):
        """
        Set text format to underline.
        """
        fmt = QTextCharFormat()
        if self.btn_underline.isChecked():
            fmt.setFontUnderline(True)
        else:
            fmt.setFontUnderline(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_strikethrough(self):
        """
        Set text format to strikethrough.
        """
        fmt = QTextCharFormat()
        if self.btn_strikethrough.isChecked():
            fmt.setFontStrikeOut(True)
        else:
            fmt.setFontStrikeOut(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_superscript(self):
        """
        Set text vertical alignment to superscript.
        """
        fmt = QTextCharFormat()
        if self.btn_superscript.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_subscript(self):
        """
        Set text vertical alignment to subscript.
        """
        fmt = QTextCharFormat()
        if self.btn_subscript.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_no_list(self):
        print("No list")

    def format_bullet_list(self):
        print("Bullet list")

    def format_dash_list(self):
        print("Dash list")

    def format_numbered_list(self):
        print("Numbered list")

    def format_roman_list(self):
        print("Roman list")

    def format_uppercase_list(self):
        print("Uppercase list")

    def format_lowercase_list(self):
        print("Lowercase list")

    def format_increase_indent(self):
        print("Increase indent")

    def format_decrease_indent(self):
        print("Decrease indent")

    def format_black_text(self):
        print("Black text")

    def format_gray_text(self):
        print("Gray text")

    def format_red_text(self):
        print("Red text")

    def format_orange_text(self):
        print("Orange text")

    def format_yellow_text(self):
        print("Yellow text")

    def format_green_text(self):
        print("Green text")

    def format_blue_text(self):
        print("Blue text")

    def format_purple_text(self):
        print("Purple text")

    def format_clear_highlight(self):
        print("Clear highlight")

    def format_red_highlight(self):
        print("Red highlight")

    def format_organge_highlight(self):
        print("Orange highlight")

    def format_yellow_highlight(self):
        print("Yellow highlight")

    def format_green_highlight(self):
        print("Green highlight")

    def format_blue_highlight(self):
        print("Blue highlight")

    def format_purple_highlight(self):
        print("Purple highlight")

    def format_gray_highlight(self):
        print("Gray highlight")

    def format_part(self):
        print("Part")

    def format_section(self):
        print("Section")

    def format_subsection(self):
        print("Subsection")

    def format_subsubsection(self):
        print("Subsubsection")

    def format_body(self):
        print("Body")

    def format_note(self):
        print("Note")
