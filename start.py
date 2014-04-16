#!/usr/bin/python
from dc import DC, DCConfig
from dc.interface import Interface
from dc.interface import resources
resources  # Surpress unused variable name
import sys
from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)
QtGui.QFontDatabase.addApplicationFont(":/fonts/DejaVuSansMono.ttf")
c = DCConfig()
d = DC(c)
i = Interface(d)
i.show()
sys.exit(app.exec_())
