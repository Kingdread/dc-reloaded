#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
This part contains QItemModels to feed the RAM-View with data from the
DC RAM
"""


from ..errors import ScriptError
from ..util import signed_value
from PyQt5 import Qt, QtCore, QtGui

ICON_SIZE = (12, 12)

class RAMStyler(Qt.QStyledItemDelegate):
    # pylint: disable=too-few-public-methods
    """
    This class is responsible for coloring different cells, e.g. the
    current stack pointer.
    """
    def __init__(self, d):
        super().__init__()
        self.d = d

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

        # Just a white box. Needed because otherwise the layout would
        # be messed up between elements with icon and elements without.
        self.empty_icon = QtGui.QPixmap(*ICON_SIZE)
        self.empty_icon.fill(QtGui.QColor(0, 0, 0, 0))

        self.breakpoint_icon = QtGui.QPixmap(*ICON_SIZE)
        self.breakpoint_icon.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter(self.breakpoint_icon)
        painter.setBrush(QtCore.Qt.red)
        painter.drawEllipse(0, 0, ICON_SIZE[0]-1, ICON_SIZE[1]-1)

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
        # Text
        if role == QtCore.Qt.DisplayRole:
            adr = index.row()
            cell = self.d.ram[adr]
            cmd = self.d.command_name(cell)
            sval = signed_value(cell, self.d.cellwidth)
            if cmd == "DEF":
                arg = sval
            else:
                arg = cell & self.d.max_address
            return("{adr:3} {cmd:4} {arg:5} | {val:0{w}b} ({sval})".format(
                adr=adr, cmd=cmd, arg=arg, val=cell, w=self.d.cellwidth,
                sval=sval))
        # Icon
        elif role == QtCore.Qt.DecorationRole:
            adr = index.row()
            icon = None
            if adr in self.d.breakpoints:
                icon = self.breakpoint_icon
            else:
                icon = self.empty_icon
            return QtCore.QVariant(icon)

    def setData(self, index, value, role):
        """
        Overwritten setData from QtCore.QAbstractItemModel
        """
        if role == QtCore.Qt.EditRole:
            if not value:
                return False
            cell = index.row()
            try:
                self.d.ram[cell] = self.d.parse_command(value)
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
