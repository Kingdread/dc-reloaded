#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from ..errors import ScriptError, AssembleError, DCError, NoInputValue
from .rammodel import RAMModel, RAMStyler
from .ui_main import Ui_DCWindow
from PyQt4 import QtGui, QtCore
import os


class Interface(QtGui.QMainWindow):
    """
    Main Window for the Graphical Interface. You have to construct
    a QApplication before you can use objects of this class!
    """
    DEFAULT_DELAY = 0.5  # in seconds
    def __init__(self, d):
        """
        Initializes the Interface. You need to pass a DC object to the
        initializer. All operations (e.g. .cycle()) will be performed
        on that object. The Interface will automatically set
        d.interface to itself.
        """
        super().__init__()
        self.d = d
        d.interface = self
        # Counter for the GUI updates. If delay is small, the GUI would
        # update way too often so we only update it every nth cycle
        # (see delay.setter)
        self.dblock = 0
        self.maxdblock = 0
        self.ui = Ui_DCWindow()
        self.ui.setupUi(self)

        self.metronome = QtCore.QTimer()
        self.metronome.setInterval(self.DEFAULT_DELAY * 1000)
        self.metronome.timeout.connect(self._runningStep)
        self.model = RAMModel(self.d)
        self.styler = RAMStyler(self.d)
        self.ui.RAM.setModel(self.model)
        self.ui.RAM.setItemDelegate(self.styler)
        self.ui.RAM.installEventFilter(self)
        self.ui.command.installEventFilter(self)
        self.ui.visual.setD(d)

        self.ui.actionClear.triggered.connect(self.clear)
        self.ui.actionOpen.triggered.connect(self.loadDialog)
        self.ui.actionRun.triggered.connect(self.startExecution)
        self.ui.actionStep.triggered.connect(self.step)
        self.ui.actionStop.triggered.connect(self.pauseExecution)
        self.ui.command.returnPressed.connect(self.execCmdline)

        self.ui.RAM.selectionModel().selectionChanged.connect(self._updatePC)
        self._selectionlock = False

        self._cmdind = 0
        self._cmdhist = []
        self.delaywarned = False
        self.gui_enabled = True
        self.lastdir = ""

    @property
    def delay(self):
        return self.metronome.interval()

    @delay.setter
    def delay(self, d):
        if d <= 0:
            raise ValueError("Delay must be greater than zero")
        self.metronome.setInterval(d * 1000)
        self.maxdblock = 0.1 / d
        self.dblock = 0

    def update(self):
        """
        Called after each cycle. This method checks if the screen
        should be updated, and if so, calls .updateScreen(). If you
        want to ensure an update, call .updateScreen() directly.
        """
        if self.gui_enabled:
            # This is important, as otherwise we'd experience great lag
            # if the delay is too small and updateScreen gets called
            # too often. Feel free to adjust the "formula" in
            # delay.setter
            if self.delay >= 0.1 or self.dblock == self.maxdblock:
                self.updateScreen()
                self.dblock = 0
            else:
                self.dblock += 1

    def report(self, error):
        """
        Logs an error on the command line and displays an error-message
        -box
        """
        self.logLine("Error: {}".format(error))
        QtGui.QMessageBox.critical(self, "Error", str(error))

    def startExecution(self):
        """
        Starts the metronome
        """
        self.d.running = True
        self.metronome.start()

    def pauseExecution(self):
        """
        Stop the metronome
        """
        self.metronome.stop()

    def step(self):
        """
        Advances the DC by a single step but only if it's not running
        """
        if not self.isRunning():
            try:
                self.d.cycle()
            except DCError as de:
                self.report(de)
            self.updateScreen()

    def _runningStep(self):
        """
        This is the function that gets executed with every metronome
        tick. It advances the DC just like .step(), but bypasses the
        check that .step(). It will also stop the metronome if the
        program reached its end.
        """
        try:
            self.d.cycle()
        except DCError as de:
            self.report(de)
        self.update()
        # Reached the end of the program:
        if not self.d.running:
            self.metronome.stop()
            self.updateScreen()

    def showOutput(self, item):
        """
        Show some output on the Log (called by the DC object)
        """
        self.logLine("Output: {}".format(item))
        # Those messages can get quite disturbing if your program procudes
        # many of those. Maybe let this commented out until there's a
        # better solution
        # QtGui.QMessageBox.information(self, "Output", str(item))

    def isRunning(self):
        """
        Returns if the program is running or not
        """
        return self.metronome.isActive()

    def _updateSelection(self):
        """
        Updates the RAM view selection to match the current value of
        the PC register.
        """
        # We need to lock here, otherwise the registered event for
        # selectionChanged will get triggered (._updatePC())
        self._selectionlock = True
        s = self.ui.RAM.selectionModel()
        s.clear()
        s.select(self.model.index(self.d.pc.value, 0, None),
                 QtGui.QItemSelectionModel.Select)
        self._selectionlock = False

    def _updateRegisters(self):
        """
        Sets the texts for the little register-value-view
        """
        d = self.d
        self.ui.valueAC.setText("{:5}".format(d.ac.signed_value))
        self.ui.valueDR.setText("{:5}".format(d.dr.signed_value))
        self.ui.valueAR.setText("{:5}".format(d.ar.value))
        self.ui.valuePC.setText("{:5}".format(d.pc.value))
        self.ui.valueSP.setText("{:5}".format(d.sp.value))
        self.ui.valueBP.setText("{:5}".format(d.bp.value))

    def updateScreen(self):
        """
        Update the Visualisation, Register-Value-View, the RAM-View and
        the currently selected item in the RAM-View

        tl;dr: Updates the screen.
        """
        self.ui.visual.repaint()
        self._updateRegisters()
        self.model.update()
        self._updateSelection()

    def getInput(self):
        """
        Used by DC to get an input value from the user
        """
        num = QtGui.QInputDialog.getInt(
            self, "Input", "Enter a value:", min=self.d.minint,
            max=self.d.maxint)
        if num[1]:
            self.logLine("Input: {}".format(num[0]))
            return num[0]
        raise NoInputValue

    def _updatePC(self, selected, deselected):
        """
        Updates the PC register to the value clicked by the user.
        """
        if not self._selectionlock:
            r = self.isRunning()
            self.pauseExecution()
            ind = selected.indexes()
            if ind:
                ind = ind[0]
                self.d.pc.set(ind.row())
                self.updateScreen()
            if r:
                self.startExecution()

    def logLine(self, line):
        """
        Logs a single line in the Log-View
        """
        self.ui.history.appendPlainText(line)

    def loadDialog(self):
        """
        Shows the dialog to load or assemble a file.
        A .dc file will get loaded, a .dcl file will get assembled
        first.
        """
        name = QtGui.QFileDialog.getOpenFileName(
            directory=self.lastdir, caption="Open file",
            filter="DC files (*.dc *.dcl)")
        if name.lower().endswith(".dc"):
            self.loadFile(name)
        elif name.lower().endswith(".dcl"):
            self.assembleFile(name)

    def loadFile(self, name):
        """
        Loads the file given by name
        """
        self.lastdir = os.path.dirname(name)
        try:
            with open(name, "r") as fo:
                content = fo.readlines()
        except IOError:
            QtGui.QMessageBox.critical(self, "Error",
                                       "Can't access {}".format(name))
            return
        try:
            self.d.load(content)
            self.logLine("Loaded {}".format(name))
            self.updateScreen()
        except ScriptError as se:
            QtGui.QMessageBox.critical(
                self, "Error",
                ("Invalid script file (maybe you forgot to assemble it?):"
                 "<br><b> {}").format(se.msg))
            return

    @staticmethod
    def _mkname(name):
        """
        Split off the filename extension and append a .dc
        """
        x = name.split(".")
        if len(x) > 1:
            return ".".join(x[:-1] + ["dc"])
        return "{}.dc".format(name)

    def assembleFile(self, name):
        """
        Assemble and load the file given by name
        """
        self.lastdir = os.path.dirname(name)
        try:
            with open(name, "r") as fo:
                content = fo.readlines()
        except IOError:
            QtGui.QMessageBox.critical(self, "Error",
                                       "Can't access {}".format(name))
            return
        try:
            assembled = self.d.assemble(content)
        except AssembleError as ae:
            QtGui.QMessageBox.critical(self, "Error", ae.msg)
            return
        self.logLine("Assembled {}".format(name))
        self.d.load(assembled)
        self.updateScreen()
        name = self._mkname(name)
        if os.access(name, os.R_OK):
            res = QtGui.QMessageBox.question(
                self, "Overwrite", ("File {} already"
                                    " exists. Overwrite it?").format(name),
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel)
            if res == QtGui.QMessageBox.Cancel:
                return
        try:
            with open(name, "w") as fo:
                fo.write("\r\n".join(assembled))
            self.logLine("Saved file to {}".format(name))
        except IOError:
            QtGui.QMessageBox.warning(
                self, "Oops",
                "Can't write the assembled"
                " file to {}. It still got loaded, but you need to assemble it"
                " again next time.".format(name))

    def execCmdline(self):
        """
        Hook executed when the user presses enter in the cmdline.
        """
        cmd = self.ui.command.text()
        self._cmdhist.append(cmd)
        self._cmdind = 0
        self.ui.command.setText("")
        if not cmd:
            self.step()
            return

        cmd = cmd.split(None, 1)
        try:
            int(cmd[0])
        except ValueError:
            self._dispatchCmd(cmd)
        else:
            try:
                self.d.load([" ".join(cmd)], False)
            except ScriptError as se:
                QtGui.QMessageBox.critical(self, "Error", se.msg)
        self.updateScreen()

    def _dispatchCmd(self, cmd):
        """
        Decide what to do with the cmd given on the cmdline
        """
        c = cmd[0].lower()
        if c in {"l", "load"}:
            try:
                name = cmd[1]
            except IndexError:
                self.loadDialog()
            else:
                self.loadFile(name)
        elif c in {"a", "ass", "asm", "assemble"}:
            try:
                name = cmd[1]
            except IndexError:
                self.assembleDialog()
            else:
                self.assembleFile(name)
        elif c in {"r", "run"}:
            self.startExecution()
        elif c in {"c", "clear"}:
            self.clear()
        elif c == "pc":
            try:
                self.d.pc.set(int(cmd[1]))
            except (ValueError, IndexError):
                QtGui.QMessageBox.warning(self, "Invalid",
                                          "pc expects an int"
                                          "eger as parameter")
        elif c in {"g", "goto"}:
            try:
                self.d.pc.set(int(cmd[1]))
                self.startExecution()
            except (ValueError, IndexError):
                QtGui.QMessageBox.warning(self, "Invalid",
                                          "goto expects an "
                                          "integer as parameter")
        elif c in {"d", "delay"}:
            try:
                delay = float(cmd[1])
                if delay <= 0:
                    raise ValueError
            except (ValueError, IndexError):
                QtGui.QMessageBox.warning(self, "Invalid", "delay must be > 0")
            else:
                self.delay = float(cmd[1])
                self.logLine("Delay set to {}".format(self.delay))
                if delay < 0.1 and not self.delaywarned:
                    self.logLine("Warning: A small delay might cause lags or a"
                                 " complete unresponsiveness of the user inter"
                                 "face!")
                    self.delaywarned = True
        elif c == "togglegui":
            self.gui_enabled = not self.gui_enabled
            self.logLine("GUI is now {}".format(
                         "enabled" if self.gui_enabled else "disabled"))
        elif c == "update":
            # actually don't call updateScreen() since it will be auto-
            # matically called in execCmdline()
            pass
        elif c == "hardcore":
            self.gui_enabled = False
            self.delay = 0.00001
            self.logLine("Hardcore simulation is now on")
        elif c == "quit":
            import sys
            sys.exit()
        else:
            QtGui.QMessageBox.warning(self, "Invalid",
                                      "Unknown command: {}".format(cmd[0]))

    def clear(self):
        """
        Reset everything.
        """
        self.pauseExecution()
        self.d.reset()
        self.gui_enabled = True
        self.delay = self.DEFAULT_DELAY
        self.ui.history.setPlainText("")
        self.updateScreen()

    def eventFilter(self, obj, event):
        """
        Event filter for some objects.
        1) RAM view, to respond to Arrow-Up/Arrow-Down key presses
        2) cmdline, to respond to Arrow-Up/Arrow-Down key presses
        """
        if obj == self.ui.RAM and event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Up:
                if not self.isRunning():
                    self.d.pc.dec()
                    self.updateScreen()
                return True
            elif key == QtCore.Qt.Key_Down:
                if not self.isRunning():
                    self.d.pc.inc()
                    self.updateScreen()
                return True

        elif obj == self.ui.command and event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Up:
                if self._cmdind < len(self._cmdhist):
                    self._cmdind += 1
                if self._cmdhist:
                    self.ui.command.setText(self._cmdhist[-1 * self._cmdind])
                return True
            elif key == QtCore.Qt.Key_Down:
                if self._cmdind > 0:
                    self._cmdind -= 1
                if self._cmdind == 0:
                    self.ui.command.setText("")
                elif self._cmdhist:
                    self.ui.command.setText(self._cmdhist[-1 * self._cmdind])
                return True

        return False
