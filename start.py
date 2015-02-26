#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Startscript for DC
"""
from dc import DC, DCConfig
from dc.interface import Interface
from dc.interface import resources #pylint: disable=unused-import
import sys
from PyQt5 import Qt, QtGui

def main():
    """DC main entry point"""
    app = Qt.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont(":/fonts/DejaVuSansMono.ttf")
    config = DCConfig()
    dc_object = DC(config)
    interface = Interface(dc_object)
    interface.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
