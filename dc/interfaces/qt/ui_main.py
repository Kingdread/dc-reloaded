# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Wed Feb 12 18:37:45 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DCWindow(object):
    def setupUi(self, DCWindow):
        DCWindow.setObjectName(_fromUtf8("DCWindow"))
        DCWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(DCWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, 10, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.visual = DCRegisterView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.visual.sizePolicy().hasHeightForWidth())
        self.visual.setSizePolicy(sizePolicy)
        self.visual.setMinimumSize(QtCore.QSize(500, 300))
        self.visual.setMaximumSize(QtCore.QSize(500, 300))
        self.visual.setObjectName(_fromUtf8("visual"))
        self.verticalLayout.addWidget(self.visual)
        self.history = QtGui.QPlainTextEdit(self.centralwidget)
        self.history.setReadOnly(True)
        self.history.setPlainText(_fromUtf8(""))
        self.history.setObjectName(_fromUtf8("history"))
        self.verticalLayout.addWidget(self.history)
        self.command = QtGui.QLineEdit(self.centralwidget)
        self.command.setObjectName(_fromUtf8("command"))
        self.verticalLayout.addWidget(self.command)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.RAM = QtGui.QListView(self.centralwidget)
        self.RAM.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans Mono"))
        self.RAM.setFont(font)
        self.RAM.setObjectName(_fromUtf8("RAM"))
        self.horizontalLayout_2.addWidget(self.RAM)
        DCWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(DCWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        DCWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(DCWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        DCWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(DCWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        DCWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionRun = QtGui.QAction(DCWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/execute.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRun.setIcon(icon)
        self.actionRun.setObjectName(_fromUtf8("actionRun"))
        self.actionStep = QtGui.QAction(DCWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/step.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStep.setIcon(icon1)
        self.actionStep.setObjectName(_fromUtf8("actionStep"))
        self.actionStop = QtGui.QAction(DCWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/stop.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStop.setIcon(icon2)
        self.actionStop.setObjectName(_fromUtf8("actionStop"))
        self.actionAssemble = QtGui.QAction(DCWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/assemble.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAssemble.setIcon(icon3)
        self.actionAssemble.setObjectName(_fromUtf8("actionAssemble"))
        self.actionOpen = QtGui.QAction(DCWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon4)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.toolBar.addAction(self.actionRun)
        self.toolBar.addAction(self.actionStep)
        self.toolBar.addAction(self.actionStop)
        self.toolBar.addAction(self.actionAssemble)
        self.toolBar.addAction(self.actionOpen)

        self.retranslateUi(DCWindow)
        QtCore.QMetaObject.connectSlotsByName(DCWindow)

    def retranslateUi(self, DCWindow):
        DCWindow.setWindowTitle(_translate("DCWindow", "DC reloaded", None))
        self.toolBar.setWindowTitle(_translate("DCWindow", "toolBar", None))
        self.actionRun.setText(_translate("DCWindow", "Run", None))
        self.actionRun.setToolTip(_translate("DCWindow", "Run the current script", None))
        self.actionRun.setShortcut(_translate("DCWindow", "Ctrl+R", None))
        self.actionStep.setText(_translate("DCWindow", "Step", None))
        self.actionStep.setToolTip(_translate("DCWindow", "One step forward", None))
        self.actionStep.setShortcut(_translate("DCWindow", "Ctrl+S", None))
        self.actionStop.setText(_translate("DCWindow", "Stop", None))
        self.actionStop.setToolTip(_translate("DCWindow", "Stops the execution", None))
        self.actionStop.setShortcut(_translate("DCWindow", "Ctrl+Esc", None))
        self.actionAssemble.setText(_translate("DCWindow", "Assemble", None))
        self.actionAssemble.setToolTip(_translate("DCWindow", "Open the assembler", None))
        self.actionAssemble.setShortcut(_translate("DCWindow", "Ctrl+A", None))
        self.actionOpen.setText(_translate("DCWindow", "open", None))
        self.actionOpen.setToolTip(_translate("DCWindow", "Open a file", None))

from dc.interfaces.qt.registerview import DCRegisterView
from . import resources

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DCWindow = QtGui.QMainWindow()
    ui = Ui_DCWindow()
    ui.setupUi(DCWindow)
    DCWindow.show()
    sys.exit(app.exec_())

