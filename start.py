#!/usr/bin/python
from dc import DC, DCConfig
from dc.interfaces.qt import QtInterface

c = DCConfig()
d = DC(c)
i = QtInterface(d)

i.run()
