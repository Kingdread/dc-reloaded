#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Module containing the tab widget
"""
from .highlight import Highlighter
from PyQt5 import Qt


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
        self.text.setFont(Qt.QFont("DejaVuSansMono"))
        self.text.textChanged.connect(self._text_changed)
        self.layout().addWidget(self.text)

        self.highlighter = Highlighter(self.text.document())

        self.modified = False

    def _text_changed(self):
        self.modified = True

    def save(self):
        """
        Re-save the file under the old filename.
        """
        if not self.filename:
            self.save_as_dialog()
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
        result = []
        for no, line in enumerate(lines):
            splitted = line.split(" ", 1)
            try:
                int(splitted[0])
            except ValueError:
                # First element is not a number, keep it
                new_line = " ".join(splitted)
            else:
                # First element is already a line number, remove it
                new_line = splitted[1]
            result.append("{} {}".format(no, new_line))
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
