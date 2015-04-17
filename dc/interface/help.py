#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from PyQt5 import Qt


class HelpWindow(Qt.QDialog):
    """A nice little help window showing a single HTML document"""
    def __init__(self, parent, content):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setLayout(Qt.QHBoxLayout())
        self.text = Qt.QTextEdit()
        self.text.setReadOnly(True)
        self.text.setHtml(content)
        self.layout().addWidget(self.text)

    def sizeHint(self):
        """Overwritten QWidget.sizeHint"""
        return Qt.QSize(640, 480)
