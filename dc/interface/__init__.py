#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Module contains the main Qt interface class
"""
from ..errors import ScriptError, AssembleError, DCError, NoInputValue
from .rammodel import RAMModel, RAMStyler
from .ui_main import Ui_DCWindow
from PyQt5 import Qt, QtCore
import os


class Interface(Qt.QMainWindow):
    # pylint: disable=too-many-instance-attributes,abstract-class-not-used
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
        self._gui_block_counter = 0
        self._gui_block_maximum = 0

        self.ui = Ui_DCWindow()
        self.ui.setupUi(self)

        self.metronome = QtCore.QTimer()
        self.metronome.setInterval(self.DEFAULT_DELAY * 1000)
        self.metronome.timeout.connect(self._metronome_step)
        self.model = RAMModel(self.d)
        self.styler = RAMStyler(self.d)
        self.ui.RAM.setModel(self.model)
        self.ui.RAM.setItemDelegate(self.styler)
        self.ui.RAM.installEventFilter(self)
        self.ui.command.installEventFilter(self)
        self.ui.visual.d = d

        self.ui.actionClear.triggered.connect(self.clear)
        self.ui.actionOpen.triggered.connect(self.show_load_dialog)
        self.ui.actionRun.triggered.connect(self.start_execution)
        self.ui.actionStep.triggered.connect(self.step)
        self.ui.actionStop.triggered.connect(self.pause_execution)
        self.ui.command.returnPressed.connect(self.exec_command_line)

        self.ui.RAM.selectionModel().selectionChanged.connect(self._update_PC)
        # The selection is locked when the execution is running because
        # selecting something in the RAM will change the program counter and
        # that is not what we want.
        self._selection_locked = False

        # Command history
        self._history = []
        self._history_index = 0

        self._delay_warning_shown = False
        self.gui_enabled = True
        self.lastdir = ""

    @property
    def delay(self):
        """
        delay is the delay between to program steps in seconds, i.e.
        the speed of execution.
        """
        return self.metronome.interval() / 1000.0

    @delay.setter
    def delay(self, new_delay):
        """
        Sets the delay
        """
        if new_delay <= 0:
            raise ValueError("Delay must be greater than zero")
        self.metronome.setInterval(new_delay * 1000)
        self._gui_block_maximum = 0.1 / new_delay
        self._gui_block_counter = 0

    def update(self):
        """
        Called after each cycle. This method checks if the screen
        should be updated, and if so, calls .update_screen(). If you
        want to ensure an update, call .update_screen() directly.
        """
        if self.gui_enabled:
            # This is important, as otherwise we'd experience great lag
            # if the delay is too small and update_screen gets called
            # too often. Feel free to adjust the "formula" in
            # delay.setter
            if (self.delay >= 0.1 or
                    self._gui_block_counter == self._gui_block_maximum):
                self.update_screen()
                self._gui_block_counter = 0
            else:
                self._gui_block_counter += 1

    def report(self, error):
        """
        Logs an error on the command line and displays an error-message
        -box
        """
        self.log_line("Error: {}".format(error))
        Qt.QMessageBox.critical(self, "Error", str(error))

    def start_execution(self):
        """
        Starts the execution of the program by starting the internal
        timer.
        """
        self.d.is_running = True
        self.metronome.start()

    def pause_execution(self):
        """
        Stops the execution of the program.
        """
        self.metronome.stop()

    def step(self):
        """
        Advances the DC by a single step but only if it's not running,
        thus this method can be used for "step-buttons" in the GUI.
        """
        if not self.is_running():
            try:
                self.d.cycle()
            except DCError as error:
                self.report(error)
            self.update_screen()

    def _metronome_step(self):
        """
        This is the function that gets executed with every metronome
        tick. It advances the DC just like .step(), but bypasses the
        check that .step(). It will also stop the metronome if the
        program reached its end.
        """
        try:
            self.d.cycle()
        except DCError as error:
            self.report(error)
        self.update()
        # Reached the end of the program:
        if not self.d.is_running:
            self.metronome.stop()
            self.update_screen()

    def show_output(self, item):
        """
        Show some output on the Log (called by the DC object)
        """
        self.log_line("Output: {}".format(item))
        # Those messages can get quite disturbing if your program procudes
        # many of those. Maybe let this commented out until there's a
        # better solution
        # Qt.QMessageBox.information(self, "Output", str(item))

    def is_running(self):
        """
        Returns if the program is running or not
        """
        return self.metronome.isActive()

    def _update_selection(self):
        """
        Updates the RAM view selection to match the current value of
        the PC register. You normally only need to call .update_screen()
        and it will take care of everything.
        """
        # We need to lock here, otherwise the registered event for
        # selectionChanged will get triggered (._update_PC())
        self._selection_locked = True
        model = self.ui.RAM.selectionModel()
        model.clear()
        model.select(self.model.index(self.d.pc.value, 0, None),
                     Qt.QItemSelectionModel.Select)
        self._selection_locked = False

    def _update_registers(self):
        """
        Sets the texts for the little register-value-view. You normally
        only need to call .update_screen() and it will take care of
        every-thing.
        """
        d = self.d
        self.ui.valueAC.setText("{:5}".format(d.ac.signed_value))
        self.ui.valueDR.setText("{:5}".format(d.dr.signed_value))
        self.ui.valueAR.setText("{:5}".format(d.ar.value))
        self.ui.valuePC.setText("{:5}".format(d.pc.value))
        self.ui.valueSP.setText("{:5}".format(d.sp.value))
        self.ui.valueBP.setText("{:5}".format(d.bp.value))

    def update_screen(self):
        """
        Update the Visualisation, Register-Value-View, the RAM-View and
        the currently selected item in the RAM-View

        tl;dr: Updates the screen.
        """
        self.ui.visual.repaint()
        self._update_registers()
        self.model.update()
        self._update_selection()

    def get_input(self):
        """
        Used by DC to get an input value from the user. Raises
        dc.errors.NoInputValue if no value is entered.
        """
        num = Qt.QInputDialog.getInt(
            self, "Input", "Enter a value:", min=self.d.min_int,
            max=self.d.max_int)
        if num[1]:
            self.log_line("Input: {}".format(num[0]))
            return num[0]
        raise NoInputValue

    def _update_PC(self, selected, deselected):
        """
        Updates the PC register to the value clicked by the user. This
        function is bound to the selectionChanged event and should not
        be called manually by the user.
        """
        if not self._selection_locked:
            was_running = self.is_running()
            self.pause_execution()
            ind = selected.indexes()
            if ind:
                ind = ind[0]
                self.d.pc.set(ind.row())
                self.update_screen()
            if was_running:
                self.start_execution()

    def log_line(self, line):
        """
        Logs a single line in the Log-View.
        """
        self.ui.history.appendPlainText(line)

    def show_load_dialog(self):
        """
        Shows the dialog to load or assemble a file.
        A .dc file will get loaded, a .dcl file will get assembled
        first.
        """
        # Returns (name, filter) as stated by the docs of PyQt5 at
        # http://pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html#qfiledialog
        name, _ = Qt.QFileDialog.getOpenFileName(
            directory=self.lastdir, caption="Open file",
            filter="DC files (*.dc *.dcl)")
        if name.lower().endswith(".dc"):
            self.load_file(name)
        elif name.lower().endswith(".dcl"):
            self.assemble_file(name)

    def load_file(self, name):
        """
        Loads the file given by name
        """
        self.lastdir = os.path.dirname(name)
        try:
            with open(name, "r") as input_file:
                content = input_file.readlines()
        except IOError:
            Qt.QMessageBox.critical(self, "Error",
                                    "Can't access {}".format(name))
            return
        try:
            self.d.load(content)
            self.log_line("Loaded {}".format(name))
            self.update_screen()
        except ScriptError as error:
            Qt.QMessageBox.critical(
                self, "Error",
                ("Invalid script file (maybe you forgot to assemble it?):"
                 "<br><b> {}").format(error.msg))

    @staticmethod
    def _assembled_name(name):
        """
        Split off the filename extension and append a .dc
        """
        splitname = name.split(".")
        if len(splitname) > 1:
            return ".".join(splitname[:-1] + ["dc"])
        return "{}.dc".format(name)

    def assemble_file(self, name):
        """
        Assemble and load the file given by name
        """
        self.lastdir = os.path.dirname(name)
        try:
            with open(name, "r") as input_file:
                content = input_file.readlines()
        except IOError:
            Qt.QMessageBox.critical(self, "Error",
                                    "Can't access {}".format(name))
            return
        try:
            assembled = self.d.assemble(content)
        except AssembleError as error:
            Qt.QMessageBox.critical(self, "Error", error.msg)
            return
        self.log_line("Assembled {}".format(name))
        self.d.load(assembled)
        self.update_screen()
        name = self._assembled_name(name)
        if os.access(name, os.R_OK):
            res = Qt.QMessageBox.question(
                self, "Overwrite", ("File {} already"
                                    " exists. Overwrite it?").format(name),
                Qt.QMessageBox.Save | Qt.QMessageBox.Cancel)
            if res == Qt.QMessageBox.Cancel:
                return
        try:
            with open(name, "w") as output_file:
                output_file.write("\r\n".join(assembled))
            self.log_line("Saved file to {}".format(name))
        except IOError:
            Qt.QMessageBox.warning(
                self, "Oops",
                "Can't write the assembled"
                " file to {}. It still got loaded, but you need to assemble it"
                " again next time.".format(name))

    def exec_command_line(self):
        """
        Hook executed when the user presses enter in the cmdline.
        """
        cmd = self.ui.command.text()
        self._history.append(cmd)
        self._history_index = 0
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
            except ScriptError as error:
                Qt.QMessageBox.critical(self, "Error", error.msg)
        self.update_screen()

    def _dispatchCmd(self, cmd):
        # pylint: disable=too-many-branches,too-many-statements
        """
        Decide what to do with the cmd given on the cmdline
        """
        order = cmd[0].lower()
        if order in {"l", "load"}:
            try:
                name = cmd[1]
            except IndexError:
                self.show_load_dialog()
            else:
                self.load_file(name)
        elif order in {"a", "ass", "asm", "assemble"}:
            try:
                name = cmd[1]
            except IndexError:
                self.show_load_dialog()
            else:
                self.assemble_file(name)
        elif order in {"r", "run"}:
            self.start_execution()
        elif order in {"c", "clear"}:
            self.clear()
        elif order == "pc":
            try:
                self.d.pc.set(int(cmd[1]))
            except (ValueError, IndexError):
                Qt.QMessageBox.warning(self, "Invalid",
                                       "pc expects an integer as parameter")
        elif order in {"g", "goto"}:
            try:
                self.d.pc.set(int(cmd[1]))
                self.start_execution()
            except (ValueError, IndexError):
                Qt.QMessageBox.warning(self, "Invalid",
                                       "goto expects an integer as parameter")
        elif order in {"d", "delay"}:
            try:
                delay = float(cmd[1])
                if delay <= 0:
                    raise ValueError
            except (ValueError, IndexError):
                Qt.QMessageBox.warning(self, "Invalid", "delay must be > 0")
            else:
                self.delay = float(cmd[1])
                self.log_line("Delay set to {}".format(self.delay))
                if delay < 0.1 and not self._delay_warning_shown:
                    self.log_line("Warning: A small delay might cause lags or "
                                  "a complete unresponsiveness of the user "
                                  "interface!")
                    self._delay_warning_shown = True
        elif order == "togglegui":
            self.gui_enabled = not self.gui_enabled
            self.log_line("GUI is now {}".format(
                "enabled" if self.gui_enabled else "disabled"))
        elif order == "update":
            # actually don't call update_screen() since it will be auto-
            # matically called in exec_command_line()
            pass
        elif order == "hardcore":
            self.gui_enabled = False
            self.delay = 0.00001
            self.log_line("Hardcore simulation is now on")
        elif order == "quit":
            import sys
            sys.exit()
        else:
            Qt.QMessageBox.warning(self, "Invalid",
                                   "Unknown command: {}".format(cmd[0]))

    def clear(self):
        """
        Reset everything.
        """
        self.pause_execution()
        self.d.reset()
        self.gui_enabled = True
        self.delay = self.DEFAULT_DELAY
        self.ui.history.setPlainText("")
        self.update_screen()

    def eventFilter(self, obj, event):
        # pylint: disable=too-many-branches
        """
        Overwrites QObject.eventFilter

        Event filter for some objects.
        1) RAM view, to respond to Arrow-Up/Arrow-Down key presses
        2) cmdline, to respond to Arrow-Up/Arrow-Down key presses
        """
        if obj == self.ui.RAM and event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Up:
                if not self.is_running():
                    self.d.pc.dec()
                    self.update_screen()
                return True
            elif key == QtCore.Qt.Key_Down:
                if not self.is_running():
                    self.d.pc.inc()
                    self.update_screen()
                return True

        elif obj == self.ui.command and event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Up:
                if self._history_index < len(self._history):
                    self._history_index += 1
                if self._history:
                    index = -1 * self._history_index
                    self.ui.command.setText(self._history[index])
                return True
            elif key == QtCore.Qt.Key_Down:
                if self._history_index > 0:
                    self._history_index -= 1
                if self._history_index == 0:
                    self.ui.command.setText("")
                elif self._history:
                    index = -1 * self._history_index
                    self.ui.command.setText(self._history[index])
                return True

        return False
