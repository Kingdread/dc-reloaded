#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
This part contains QItemModels to feed the RAM-View with data from the
DC RAM
"""


from ..errors import ScriptError
from ..util import signed_value
from PyQt5 import Qt, QtCore, QtGui


class RAMStyler(Qt.QStyledItemDelegate):
    # pylint: disable=too-few-public-methods
    """
    This class is responsible for coloring different cells, e.g. the
    current stack pointer.
    """
    def __init__(self, d):
        super().__init__()
        self.d = d
        self.i = 0

    def initStyleOption(self, option, index):
        """
        Overwritten initStyleOption from Qt.QStyledItemDelegate
        """
        super().initStyleOption(option, index)
        if index.row() == self.d.sp.value:
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            option.font.setBold(True)
        elif index.row() in self.d.return_addresses:
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.blue)


class RAMModel(QtCore.QAbstractItemModel):
    # pylint: disable=no-self-use
    """
    This model provides access to the DC RAM via a QItemModel
    """
    def __init__(self, d):
        super().__init__()
        self.d = d

    def index(self, row, column, parent_):
        """
        Overwritten index from QtCore.QAbstractItemModel
        """
        return self.createIndex(row, column)

    def parent(self, index_):
        """
        Overwritten parent from QtCore.QAbstractItemModel
        """
        return QtCore.QModelIndex()

    def rowCount(self, index_):
        """
        Overwritten rowCount from QtCore.QAbstractItemModel
        """
        return len(self.d.ram)

    def columnCount(self, index_):
        """
        Overwritten columnCount from QtCore.QAbstractItemModel
        """
        return 1

    def data(self, index, role):
        """
        Overwritten data from QtCore.QAbstractItemModel
        """
        if role == QtCore.Qt.DisplayRole:
            adr = index.row()
            cell = self.d.ram[adr]
            cmd = self.d.getcmd(cell)
            sval = signed_value(cell, self.d.cellwidth)
            if cmd == "DEF":
                arg = sval
            else:
                arg = cell & self.d.max_address
            return("{adr:3} {cmd:4} {arg:5} | {val:0{w}b} ({sval})".format(
                adr=adr, cmd=cmd, arg=arg, val=cell, w=self.d.cellwidth,
                sval=sval))

    def setData(self, index, value, role):
        """
        Overwritten setData from QtCore.QAbstractItemModel
        """
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

    def flags(self, index_):
        """
        Overwritten flags from QtCore.QAbstractItemModel
        """
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
