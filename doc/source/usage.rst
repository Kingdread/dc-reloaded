Using DC reloaded
=================

.. note::

   This page is about the usage of the program. The
   :doc:`theory/instruction set </hardware>` is covered later in this
   documentation.

The DC main window consists of three main parts:

* The visualization: top-left
* The command line: bottom-left
* The memory: right

The visualization just shows the state of the registers during the
execution. It doesn't provide any interaction (yet).

The memory view shows the contents of the RAM and hightlights the cell
currently pointed to by the program counter, colors the current stack
position and function return addresses.

The command line provides a simple interface to control DC.

Changing the content of a RAM cell
----------------------------------

There are two ways to change the content of a RAM cell, either
double-click the cell in the memory and edit the contents, or enter
``<cell-no> <content>`` into the command line, e.g. if you want the
command ``JMP 42`` in cell 13, enter ``13 JMP 42`` and press enter.

This way you can enter programs, but doing that over and over again
would be tedious, that's why there is a way to...

Load a file
-----------

To open the file dialog, simply click the "open a file" button in the
toolbar. Alternatively, you can enter ``load`` in the command line,
optionally followed by the file name.

Files ending in .dc are treated as "raw dc files", while .dcl files
are treated as "assembly dc files". .dcl files are automatically
assembled when loaded and saved as name.dc (if not yet existing).

Controlling the exectution
--------------------------

The first three buttons in the toolbar stand for start, single-step
and stop. Using the command line, the command ``run`` is
available. For a single step enter an empty command (i.e. just press
enter while the command line is focused).

Command line commands
---------------------

Parameters in brackets ([]) are optional, names in parentheses after
the command name are the command aliases.

.. rubric:: load(l) *[filename]*

Loads the given .dc file. If no filename is specified, a file dialog
will appear.

.. rubric:: assemble(a, ass, asm) *[filename]*

Assemble the given .dcl file. If no filename is specified, a file
dialog will appear.

.. rubric:: run(r)

Start the execution.

.. rubric:: clear(c)

Reset the simulator to its initial state.

.. rubric:: pc *cell*

Set the program counter register to the given value. This is like a
jump instruction.

.. rubric:: goto(g) *cell*

The same as ``pc`` followed by ``run``.

.. rubric:: delay(d) *delay*

Set the waiting delay between to statements. The lower this delay is,
the faster the program executes.

.. rubric:: togglegui

Enable/disable the visualization. Good if you want more performance
with small delays.

.. rubric:: update

Update the screen, useful if the GUI is disabled.

.. rubric:: hardcore

Sets a very small delay and disables the GUI for a good performance.

.. warning:: The program might feel "laggy" when using low delays or
             hardcore mode!

.. rubric:: quit

Exits the program.
