from dc.interfaces.qt.ui_main import Ui_DCWindow
from dc.interfaces.qt.rammodel import RAMModel
from dc.errors import ScriptError, AssembleError
from PyQt4 import QtGui, QtCore
from queue import Empty
import os

class DCWindow(QtGui.QMainWindow):
    updateScreen = QtCore.pyqtSignal()
    getInput = QtCore.pyqtSignal()
    showOutput = QtCore.pyqtSignal()

    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self.ui = Ui_DCWindow()
        self.ui.setupUi(self)

        self.model = RAMModel(self.interface.d)
        self.ui.RAM.setModel(self.model)

        self.ui.actionRun.triggered.connect(self.interface.startExecution)
        self.ui.actionStep.triggered.connect(self.interface.step)
        self.ui.actionStop.triggered.connect(self.interface.pauseExecution)
        self.ui.actionOpen.triggered.connect(self.loadDialog)
        self.ui.actionAssemble.triggered.connect(self.assembleDialog)
        self.ui.command.returnPressed.connect(self.execCmdline)

        self.ui.RAM.selectionModel().selectionChanged.connect(self._updatePC)
        self._selectionlock = False

        self.getInput.connect(self._getInput)
        self.showOutput.connect(self._showOutput)
        
        self.updateScreen.connect(self._updateScreen)

    def _updateSelection(self):
        self._selectionlock = True
        s = self.ui.RAM.selectionModel()
        s.clear()
        s.select(self.model.index(self.interface.d.pc.value, 0, None), QtGui.QItemSelectionModel.Select)
        self._selectionlock = False

    def _updateRegisters(self):
        d = self.interface.d
        self.ui.valueAC.setText(str(d.ac.signed_value))
        self.ui.valueDR.setText(str(d.dr.signed_value))
        self.ui.valueAR.setText(str(d.ar.value))
        self.ui.valuePC.setText(str(d.pc.value))
        self.ui.valueSP.setText(str(d.sp.value))
        self.ui.valueBP.setText(str(d.bp.value))

    def _updateScreen(self):
        self.ui.visual.repaint()
        self._updateRegisters()
        self.model.update()
        self._updateSelection()

    def _getInput(self):
        num = QtGui.QInputDialog.getInt(self, "Input", "Enter a value:", min=-4096, max=4095)
        if num[1]:
            self.logLine("Input: {}".format(num[0]))
        self.interface.inputq.put(num)

    def _showOutput(self):
        while True:
            try:
                item = self.interface.outq.get(block=False)
            except Empty:
                break
            self.logLine("Output: {}".format(item))
            # Those messages can get quite disturbing if your program procudes
            # many of those. Maybe let this commented out until there's a 
            # better solution
            # QtGui.QMessageBox.information(self, "Output", str(item))
    
    def _updatePC(self, selected, deselected):
        if not self._selectionlock:
            r = self.interface.isRunning()
            self.interface.pauseExecution()
            ind = selected.indexes()
            if ind:
                ind = ind[0]
                self.interface.d.pc.set(ind.row())
                self._updateScreen()
            if r:
                self.interface.startExecution()

    def logLine(self, line):
        self.ui.history.appendPlainText(line)

    def loadDialog(self):
        name = QtGui.QFileDialog.getOpenFileName()
        if name:
            self.loadFile(name)

    def loadFile(self, name):
        try:
            with open(name, "r") as fo:
                content = fo.readlines()
        except IOError:
            QtGui.QMessageBox.critical(self, "Error", "Can't access {}".format(name))
            return
        try:
            self.interface.d.load(content)
            self.logLine("Loaded {}".format(name))
            self._updateScreen()
        except ScriptError as se:
            QtGui.QMessageBox.critical(self, "Error",
              "Invalid script file (maybe you forgot to assemble it?):<br><b> {}".format(se.msg))
            return

    @staticmethod
    def _mkname(name):
        x = name.split(".")
        if len(x) > 1:
            return ".".join(x[:-1] + ["dc"])
        return "{}.dc".format(name)

    def assembleDialog(self):
        name = QtGui.QFileDialog.getOpenFileName()
        if name:
            self.assembleFile(name)

    def assembleFile(self, name):
        try:
            with open(name, "r") as fo:
                content = fo.readlines()
        except IOError:
            QtGui.QMessageBox.critical(self, "Error", "Can't access {}".format(name))
            return
        try:
            assembled = self.interface.d.assemble(content)
        except AssembleError as ae:
            QtGui.QMessageBox.critical(self, "Error", ae.msg)
            return
        self.logLine("Assembled {}".format(name))
        self.interface.d.load(assembled)
        name = self._mkname(name)
        if os.access(name, os.R_OK):
            res = QtGui.QMessageBox.question(self, "Overwrite", "Filel {} already"
              " exists. Overwrite it?".format(name),
              QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel)
            if res == QtGui.QMessageBox.Cancel:
                return
        try:
            with open(name, "w") as fo:
                fo.write("\r\n".join(assembled))
            self.logLine("Saved file to {}".format(name))
        except IOError:
            QtGui.QMessageBox.warning(self, "Oops", "Can't write the assembled"
              " file to {}. It still got loaded, but you need to assemble it "
              "again next time.".format(name))

    def execCmdline(self):
        cmd = self.ui.command.text()
        self.ui.command.setText("")
        if not cmd:
            self.interface.step()
            return

        cmd = cmd.split()
        try:
            adr = int(cmd[0])
        except ValueError:
            self._dispatchCmd(cmd)
        else:
            self.interface.d.load([" ".join(cmd)], False)
        self._updateScreen()

    def _dispatchCmd(self, cmd):
        c = cmd[0] = cmd[0].lower()

        if c in {"l", "load"}:
            try:
                name = cmd[1]
            except IndexError:
                self.loadDialog()
            else:
                self.loadFile(name)
        elif c in {"a", "ass", "assemble"}:
            try:
                name = cmd[1]
            except IndexError:
                self.assembleDialog()
            else:
                self.assembleFile(name)
        elif c in {"r", "run"}:
            self.interface.startExecution()
        elif c in {"c", "clear"}:
            self.interface.pauseExecution()
            self.interface.d.reset()
            self.ui.history.setPlainText("")
            self.logLine("Cleared")
        elif c == "pc":
            try:
                self.interface.d.pc.set(int(cmd[1]))
            except (ValueError, IndexError):
                QtGui.QMessageBox.warning(self, "Invalid", "pc expects an int"
                  "eger as parameter")
        elif c in {"g", "goto"}:
            try:
                self.interface.d.pc.set(int(cmd[1]))
                self.interface.startExecution()
            except (ValueError, IndexError):
                QtGui.QMessageBox.warning(self, "Invalid", "goto expects an "
                  "integer as parameter")
        elif c in {"d", "delay"}:
            try:
                delay = float(cmd[1])
                if delay <= 0:
                    raise ValueError
            except (ValueError, IndexError):
                QtGui.QMessageBox.warning(self, "Invalid", "delay expects a"
                  " decimal > 0 as parameter")
            else:
                self.interface.delay = float(cmd[1])
                self.logLine("Delay set to {}".format(self.interface.delay))
