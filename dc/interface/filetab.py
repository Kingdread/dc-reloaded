#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Module containing the tab widget
"""
from .highlight import Highlighter
from .. import util
from .. import DC
from PyQt5 import Qt, QtCore


class FileTab(Qt.QWidget):
    """
    This is a tab for a single file. They get created by the editor
    window, each tab represents a seperate file.
    """
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.setLayout(Qt.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.text = Qt.QPlainTextEdit()
        self.text.setStyleSheet("""
        QPlainTextEdit {
            background: white;
            color: black;
        }
        """)
        self.text.setFont(Qt.QFont("DejaVu Sans Mono"))
        self.text.textChanged.connect(self._text_changed)
        self.text.cursorPositionChanged.connect(self.highlight_current_line)
        self.highlight_current_line()
        self.layout().addWidget(self.text)

        self.highlighter = Highlighter(self.text.document())
        self.line_numbers = LineNumberWidget(self.text)

        self.modified = False

    def _text_changed(self):
        """
        Function called when the text has changed. Sets the modified flag
        """
        if not self.text.toPlainText() and self.filename is None:
            return
        self.modified = True

    def save(self):
        """
        Re-save the file under the old filename.
        """
        if not self.filename:
            self.save_as()
            return
        with open(self.filename, "w") as output_file:
            output_file.write(self.text.toPlainText())
        self.modified = False

    def save_as(self):
        """
        Save the file but ask for a new filename first.
        """
        filename, _ = Qt.QFileDialog.getSaveFileName(self)
        if not filename:
            return
        with open(filename, "w") as output_file:
            output_file.write(self.text.toPlainText())
        self.filename = filename
        self.modified = False

    def fix_line_numbers(self):
        """
        Remove each line number and add them back automatically, starting with
        0
        """
        text = self.text.toPlainText()
        lines = text.split("\n")
        number = 0
        result = []
        for line in lines:
            stripped = DC.strip_comment(line).strip()
            if not stripped:
                # An empty line doesn't deserve a number but we still
                # need to include it. Same with comment only lines
                result.append(line)
                continue
            splitted = line.split(" ", 1)
            try:
                int(splitted[0])
            except ValueError:
                # First element is not a number, keep it
                new_line = " ".join(splitted)
            else:
                # First element is already a line number, remove it
                new_line = splitted[1]
            result.append("{} {}".format(number, new_line))
            number += 1
        self.text.setPlainText("\n".join(result))

    def try_reload(self):
        """
        Try to reload the file from disk. Returns True if the file could be
        successfully loaded, False otherwise.
        """
        if not self.filename:
            return False
        try:
            with open(self.filename, "r") as input_file:
                self.text.setPlainText(input_file.read())
        except IOError:
            return False
        else:
            self.modified = False
            return True

    def highlight_current_line(self):
        """
        Called when the cursor changes to highlight the current line
        """
        color = Qt.QColor(QtCore.Qt.cyan).lighter(160)
        selection = Qt.QTextEdit.ExtraSelection()
        selection.format.setBackground(color)
        selection.format.setProperty(Qt.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.text.textCursor()
        selection.cursor.clearSelection()
        self.text.setExtraSelections([selection])

    def highlight_error_line(self, line_number):
        """
        Highlight the given line to mark it as erroneous
        """
        color = Qt.QColor(QtCore.Qt.red).lighter(140)
        selection = Qt.QTextEdit.ExtraSelection()
        selection.format.setBackground(color)
        selection.format.setProperty(Qt.QTextFormat.FullWidthSelection, True)
        block = self.text.document().findBlockByNumber(line_number)
        cursor = Qt.QTextCursor(block)
        selection.cursor = cursor
        self.text.setExtraSelections([selection])


class LineNumberWidget(Qt.QWidget):
    """
    A widget providing line numbers for a TextWidget
    """
    MARGIN_RIGHT = 3
    MARGIN_LEFT = 3
    BACKGROUND_COLOR = QtCore.Qt.darkCyan
    TEXT_COLOR = QtCore.Qt.white

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_area)
        self.editor.installEventFilter(self)

        self.update_width(0)

    def eventFilter(self, obj, event):
        """
        Overwritten eventFilter to get the ResizeEvent for the editor.
        """
        if obj == self.editor and event.type() == Qt.QEvent.Resize:
            self.update_width(0)
        return False

    def paintEvent(self, event):
        """
        Overwritten paintEvent to draw the numbers.
        """
        painter = Qt.QPainter(self)
        painter.fillRect(event.rect(), self.BACKGROUND_COLOR)

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block)
        top = top.translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.TEXT_COLOR)
                painter.drawText(
                    0, top, self.width() - self.MARGIN_RIGHT,
                    self.editor.fontMetrics().height(), QtCore.Qt.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

    def calculate_width(self):
        """
        Calculate the width of the widget based on the hightest line number.
        The returned value already contains the margins.
        """
        max_number = max(1, self.editor.blockCount())
        digits = util.number_of_digits(max_number, 10)
        width = self.editor.fontMetrics().width("9") * digits
        return width + self.MARGIN_RIGHT + self.MARGIN_LEFT

    def update_width(self, count_):
        """
        Update the parent's margin and the own width. The _count parameter is
        ignored, but provided because the blockCountChanged event sends it.
        """
        self.editor.setViewportMargins(self.calculate_width(), 0, 0, 0)
        content_rect = self.editor.contentsRect()
        self.setGeometry(Qt.QRect(
            content_rect.left(),
            content_rect.top(),
            self.calculate_width(),
            content_rect.height(),
        ))

    def update_area(self, rect, delta_y):
        """
        Update the area when the widget is scrolled.
        """
        if delta_y:
            self.scroll(0, delta_y)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.update_width(0)
