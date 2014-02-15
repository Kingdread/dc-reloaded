from dc.errors import ScriptError
from PyQt4 import QtCore

def signed_value(val, bits):
    leftmost = val >> (bits - 1)
    if leftmost:
        val = (~(val - 1)) & (2 ** bits - 1)
        val = -1 * val
    return val

class RAMModel(QtCore.QAbstractItemModel):
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
            except ScriptError as se:
                return False
            self.dataChanged.emit(index, index)
            return True
    
    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsEditable)

    def update(self):
        self.dataChanged.emit(self.index(0, 0, None), self.index(len(self.d.ram)-1, 0, None))

