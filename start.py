#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from dc import DC, DCConfig
from dc.interface import Interface, resources
resources  # Surpress unused variable name
import sys
from PyQt5 import Qt, QtGui

app = Qt.QApplication(sys.argv)
QtGui.QFontDatabase.addApplicationFont(":/fonts/DejaVuSansMono.ttf")
c = DCConfig()
d = DC(c)
i = Interface(d)
i.show()
sys.exit(app.exec_())
