#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""
Module containing the editor window
"""
from .ui_editor import Ui_Editor
from .filetab import FileTab
from ..errors import DCError
from PyQt5 import Qt
import os


class Editor(Qt.QMainWindow):
    """
    Every instance of this represents an editor window. Since the editor
    is tabbed, you probably need only one of this
    """

    # Filename used by File -> New
    NEW_FILE_NAME = "New File"

    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self.dc_object = interface.d
        self.ui = Ui_Editor()
        self.ui.setupUi(self)
        self.new_tab_icon = Qt.QIcon.fromTheme("document-properties")

        self.ui.tabs.tabCloseRequested.connect(self.close_tab)
        self.ui.actionNew.triggered.connect(self.create_new_file)
        self.ui.actionSave.triggered.connect(self.save_current_tab)
        self.ui.actionSave_as.triggered.connect(self.save_current_tab_as)
        self.ui.actionOpen.triggered.connect(self.open_file_dialog)
        self.ui.actionEnumerate.triggered.connect(self.enumerate_current)
        self.ui.actionTransfer.triggered.connect(self.transfer_to_simulator)

    def create_new_file(self):
        """
        Create a new empty file in a new tab without a filename.
        """
        tab = FileTab(None)
        self.ui.tabs.addTab(tab, self.new_tab_icon, self.NEW_FILE_NAME)
        self.ui.tabs.setCurrentIndex(self.ui.tabs.count() - 1)

    def open_file_dialog(self):
        """
        Show the open file dialog.
        """
        filename, _ = Qt.QFileDialog.getOpenFileName(self)
        if not filename:
            return
        self.open_new_tab(filename)

    def open_new_tab(self, filename):
        """
        Open the given file in a new tab.
        """
        # Check if the filename is already openend in a tab, if yes,
        # then switch to that tab instead
        for i in range(self.ui.tabs.count()):
            tab = self.ui.tabs.widget(i)
            if tab.filename == filename:
                self.ui.tabs.setCurrentIndex(i)
                return
        tab_text = os.path.basename(filename)
        tab = FileTab(filename)
        tab.try_reload()
        self.ui.tabs.addTab(tab, self.new_tab_icon, tab_text)
        self.ui.tabs.setCurrentIndex(self.ui.tabs.count() - 1)
        if filename:
            self.ui.tabs.setTabToolTip(self.ui.tabs.count() - 1, filename)

    def close_tab(self, index):
        """
        Event handler to close the given tab at the index. Will prompt first if
        the file contains unsaved changes.
        """
        tab = self.ui.tabs.widget(index)
        if tab.modified:
            buttons = Qt.QMessageBox.Yes | Qt.QMessageBox.Cancel
            choice = Qt.QMessageBox.warning(self, "Unsaved changes",
                                            "This file contains unsaved "
                                            "changes. Quit anyway?", buttons)
            if choice == Qt.QMessageBox.Cancel:
                return
        self.ui.tabs.removeTab(index)

    def save_current_tab(self):
        """
        Save the current tab. Will not ask for a new filename unless it's the
        first time the file is saved.
        """
        tab = self.ui.tabs.currentWidget()
        if tab is None:
            return
        try:
            tab.save()
        except IOError as error:
            Qt.QMessageBox.critical(self, "Error",
                                    "Couldn't save: {}".format(error))
        else:
            # This might seem unnecessary, but if the file is saved for
            # the first time, the name will change and we have to update
            # the tab text
            tab_text = os.path.basename(tab.filename)
            self.ui.tabs.setTabText(self.ui.tabs.currentIndex(), tab_text)
            self.ui.tabs.setTabToolTip(self.ui.tabs.currentIndex(),
                                       tab.filename)

    def save_current_tab_as(self):
        """
        Save the current tab but prompt for a new name first.
        """
        tab = self.ui.tabs.currentWidget()
        if tab is None:
            return
        try:
            tab.save_as()
        except IOError as error:
            Qt.QMessageBox.critical(self, "Error",
                                    "Couldn't save: {}".format(error))
        else:
            tab_text = os.path.basename(tab.filename)
            self.ui.tabs.setTabText(self.ui.tabs.currentIndex(), tab_text)

    def enumerate_current(self):
        """
        Fix the line numbers in the currently selected tab
        """
        tab = self.ui.tabs.currentWidget()
        if tab is None:
            return
        tab.fix_line_numbers()

    def closeEvent(self, event):
        """
        Overwritten to provide a prompt if there are unsaved changes.
        """
        for i in range(self.ui.tabs.count()):
            tab = self.ui.tabs.widget(i)
            if tab.modified:
                buttons = Qt.QMessageBox.Yes | Qt.QMessageBox.Cancel
                choice = Qt.QMessageBox.warning(self, "Unsaved changes",
                                                "There are files that have uns"
                                                "aved changes. Quit anyway?",
                                                buttons)
                # We don't have to ask for every modified file we find,
                # either we get a yes or no
                if choice == Qt.QMessageBox.Cancel:
                    event.ignore()
                    return
                break
        self.ui.tabs.clear()
        event.accept()

    def transfer_to_simulator(self):
        """
        Transfer the currently focused program to the simulator. Does not
        require a save.
        """
        tab = self.ui.tabs.currentWidget()
        if tab is None:
            return
        lines = tab.text.toPlainText().split("\n")
        error = None
        try:
            self.dc_object.load(lines)
        except DCError:
            # That's okay, maybe we need to assemble it first
            try:
                assembled = self.dc_object.assemble(lines)
            except DCError as exc_error:
                error = exc_error
            else:
                try:
                    self.dc_object.load(assembled)
                except DCError as exc_error:
                    error = exc_error
        if error is None:
            self.interface.update_screen()
            self.interface.raise_()
        else:
            if error.line_number is not None:
                tab.highlight_error_line(error.line_number)
            Qt.QMessageBox.critical(self, "Error", str(error))
