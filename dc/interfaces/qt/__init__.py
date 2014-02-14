from dc import NoInputValue
from dc.interfaces import Interface
from dc.interfaces.qt.window import DCWindow
from dc.interfaces.qt.background import DCThread
from dc.interfaces.qt import resources
from PyQt4 import QtGui, QtCore
from queue import Queue

class QtInterface(Interface):
    def __init__(self, d):
        self.d = d
        d.interface = self
        self.window = None
        self.delay = 0.1
        self.dblock = 0
        self.thread = DCThread(self)
        self.thread.pause()
        self.thread.start()

        self.inputq = Queue()
        self.outq = Queue()
        self.errorq = Queue()
    
    def run(self):
        import sys
        app = QtGui.QApplication(sys.argv)
        QtGui.QFontDatabase.addApplicationFont(":/fonts/DejaVuSansMono.ttf")
        window = self.window = DCWindow(self)
        window.ui.visual.setD(self.d)
        window.show()
        sys.exit(app.exec_())
    
    def update(self):
        if self.window:
            if self.delay >= 0.1 or self.dblock == 10:
                self.window.updateScreen.emit()
                self.dblock = 0
            else:
                # This is important, as otherwise we'd experience great lag
                # if the delay is too small and updateScreen gets called
                # too often. Feel free to adjust the limit
                self.dblock += 1

    def report(self, error):
        self.errorq.put(error)
        self.window.showErrors.emit()

    def startExecution(self):
        self.thread.resume()

    def pauseExecution(self):
        self.thread.pause()

    def step(self):
        self.d.cycle()
        self.window.updateScreen.emit()

    def getInput(self):
        walking = self.thread._r.is_set()
        self.thread.pause()
        self.window.getInput.emit()
        i = self.inputq.get()
        if i[1]:
            if walking:
                self.thread.resume()
            return i[0]
        else:
            raise NoInputValue

    def showOutput(self, nr):
        self.outq.put(nr)
        self.window.showOutput.emit()

    def isRunning(self):
        return self.thread._r.is_set()
