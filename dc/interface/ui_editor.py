# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resource-files/editor.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Editor(object):
    def setupUi(self, Editor):
        Editor.setObjectName("Editor")
        Editor.resize(800, 600)
        Editor.setDocumentMode(True)
        self.centralwidget = QtWidgets.QWidget(Editor)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setObjectName("tabs")
        self.horizontalLayout.addWidget(self.tabs)
        Editor.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Editor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 19))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        Editor.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Editor)
        self.statusbar.setObjectName("statusbar")
        Editor.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(Editor)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(Editor)
        icon = QtGui.QIcon.fromTheme("document-save")
        self.actionSave.setIcon(icon)
        self.actionSave.setObjectName("actionSave")
        self.actionEnumerate = QtWidgets.QAction(Editor)
        icon = QtGui.QIcon.fromTheme("insert-text")
        self.actionEnumerate.setIcon(icon)
        self.actionEnumerate.setObjectName("actionEnumerate")
        self.actionNew = QtWidgets.QAction(Editor)
        icon = QtGui.QIcon.fromTheme("document-new")
        self.actionNew.setIcon(icon)
        self.actionNew.setObjectName("actionNew")
        self.actionSave_as = QtWidgets.QAction(Editor)
        self.actionSave_as.setObjectName("actionSave_as")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionEnumerate)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(Editor)
        self.tabs.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Editor)

    def retranslateUi(self, Editor):
        _translate = QtCore.QCoreApplication.translate
        Editor.setWindowTitle(_translate("Editor", "Editor"))
        self.menuFile.setTitle(_translate("Editor", "File"))
        self.actionOpen.setText(_translate("Editor", "Open"))
        self.actionSave.setText(_translate("Editor", "Save"))
        self.actionEnumerate.setText(_translate("Editor", "Fix line numbers"))
        self.actionNew.setText(_translate("Editor", "New"))
        self.actionSave_as.setText(_translate("Editor", "Save as..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Editor = QtWidgets.QMainWindow()
    ui = Ui_Editor()
    ui.setupUi(Editor)
    Editor.show()
    sys.exit(app.exec_())

