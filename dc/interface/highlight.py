#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Module containing editor highlighting related classes and functions
"""
from .. import DC
from PyQt5 import Qt, QtCore
import re


class Highlighter(Qt.QSyntaxHighlighter):
    """
    A subclass of QSyntaxHighlighter to provide basic syntax highlighting
    for DC programs
    """
    def __init__(self, document):
        super().__init__(document)
        self.comment_style = Qt.QTextCharFormat()
        self.comment_style.setForeground(QtCore.Qt.darkGray)
        self.comment_style.setFontItalic(True)

        self.number_re = re.compile(r"\b\d+\b")
        self.number_style = Qt.QTextCharFormat()
        self.number_style.setForeground(QtCore.Qt.darkGreen)

        keywords = list(DC.opcodes.keys())
        keyword_re_expr = r"\b(" + "|".join(keywords) + r")\b"
        self.keyword_re = re.compile(keyword_re_expr, re.I)
        self.keyword_style = Qt.QTextCharFormat()
        self.keyword_style.setForeground(QtCore.Qt.darkBlue)
        self.keyword_style.setFontWeight(Qt.QFont.Bold)

        self.def_re = re.compile(r"\bDEF\b", re.I)
        self.def_style = Qt.QTextCharFormat()
        self.def_style.setForeground(QtCore.Qt.blue)
        self.def_style.setFontUnderline(True)

        self.label_re = re.compile(r"\b\w+:")
        self.label_style = Qt.QTextCharFormat()
        self.label_style.setForeground(QtCore.Qt.darkMagenta)

        self.equal_re = re.compile(r"\bEQUAL\b", re.I)
        self.equal_style = Qt.QTextCharFormat()
        self.equal_style.setForeground(QtCore.Qt.darkRed)
        self.equal_style.setFontItalic(True)

    def highlightBlock(self, text):
        """
        Overwritten to provide syntax highlighting for DC programs
        """
        # Looks like text is always the current line, since we don't
        # have multi-line comments we should be fine without state
        comment = text.find(";")
        if comment != -1:
            length = len(text) - comment
            self.setFormat(comment, length, self.comment_style)
            # We don't want to highlight code in comments, so we just remove
            # everything after the comment delimiter
            text = text[:comment]

        styles = [
            (self.number_re, self.number_style),
            (self.keyword_re, self.keyword_style),
            (self.def_re, self.def_style),
            (self.label_re, self.label_style),
            (self.equal_re, self.equal_style),
        ]
        for regex, style in styles:
            matches = regex.finditer(text)
            for match in matches:
                span = match.span()
                start = span[0]
                length = span[1] - start
                self.setFormat(start, length, style)
