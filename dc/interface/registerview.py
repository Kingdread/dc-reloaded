#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
This class contains the classes needed for the visualisation of the
registers.
"""

from PyQt5 import Qt, QtCore, QtGui


class DCRegisterView(Qt.QWidget):
    # pylint: disable=too-few-public-methods
    """
    A QWidget that draws the text for the registers onto the right
    positions on the background.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.d = None  # will be set by the interface
        self.background = QtGui.QImage(":/images/bg.png")

    def paintEvent(self, event_):
        """
        Overwritten paintEvent of Qt.QWidget
        """
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.background)
        if self.d is None:
            return
        painter.setPen(QtCore.Qt.white)
        painter.setFont(QtGui.QFont("DejaVuSansMono", 13))

        painter.drawText(30, 135, self.d.sp.bin)
        painter.drawText(30, 150, self.d.bp.bin)
        painter.drawText(105, 80, self.d.pc.bin)
        ir = self.d.ir.bin
        ind = self.d.conf.control_bits
        first, second = ir[:ind], ir[ind:]
        painter.drawText(15, 255, "{}  {}".format(first, second))
        painter.drawText(255, 65, self.d.ac.bin)
        painter.drawText(400, 100, self.d.ar.bin)
        painter.drawText(342, 245, self.d.dr.bin)
