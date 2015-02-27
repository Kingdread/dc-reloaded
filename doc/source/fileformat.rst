DC file format
==============

DC supports two different but similar file formats

.dc files
---------

.dc files are pretty much a raw dump of the memory content, for example an
infinite looping program that prints 1, 1, 1, ...::

    0 DEF 1
    1 OUT 0
    2 JMP 1

The syntax of a line thus is::

    <cell no> <instruction> [<operand>]

Whereas operand is not required for some commands. Comments are introduced with
``;``, e.g.::

    ; full line comment
    0 DEF 42 ; the universal constant

.dcl files
----------

DC has a built-in little assembly language which makes writing programs a little
easier. Thus writing .dcl files is the preferred way to write programs
for DC. The assembler has the following advantages over .dc files:

* No need to manually enumerate each cell
* Support for labels with the NAME: syntax
* Constant definition with EQUALS (note that this is like a C macro that gets
  expanded at compile time, not a run time constant because run time constants
  have to be defined in a memory cell somewhere)

For example the program from above in DC assembly could look like this::

    VALUE: DEF 1
    LOOP:
    OUT VALUE
    JMP LOOP
