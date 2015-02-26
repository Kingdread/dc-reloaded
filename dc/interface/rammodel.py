#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from ..errors import ScriptError
from ..util import signed_value
from PyQt5 import Qt, QtCore, QtGui

"""
This part contains QItemModels to feed the RAM-View with data from the
DC RAM
"""


class RAMStyler(Qt.QStyledItemDelegate):
    """
    This class is responsible for coloring different cells, e.g. the
    current stack pointer.
    """
    def __init__(self, d):
        super().__init__()
        self.d = d
        self.i = 0

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if index.row() == self.d.sp.value:
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            option.font.setBold(True)
        elif index.row() in self.d.retaddrs:
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.blue)


class RAMModel(QtCore.QAbstractItemModel):
    """
    This model provides access to the DC RAM via a QItemModel
    """
    def __init__(self, d):
        super().__init__()
        self.d = d

    def index(self, row, column, parent):
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, index):
        return len(self.d.ram)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            adr = index.row()
            cell = self.d.ram[adr]
            cmd = self.d.getcmd(cell)
            sval = signed_value(cell, self.d.cellwidth)
            if cmd == "DEF":
                arg = sval
            else:
                arg = cell & self.d.maddr
            return("{adr:3} {cmd:4} {arg:5} | {val:0{w}b} ({sval})".format(
                adr=adr, cmd=cmd, arg=arg, val=cell, w=self.d.cellwidth,
                sval=sval))

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if not value:
                return False
            cell = index.row()
            try:
                self.d.ram[cell] = self.d.parsecmd(value)
            except ScriptError:
                return False
            self.dataChanged.emit(index, index)
            return True

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsEditable)

    def update(self):
        """
        Shortcut to emit the dataChanged signal and trigger an update
        of the view.
        """
        self.dataChanged.emit(self.index(0, 0, None),
                              self.index(len(self.d.ram)-1, 0, None))
