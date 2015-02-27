DC hardware description
=======================

(This is mostly a translation of `the short DC manual`_ [PDF, german])

The DC simulates a simple CPU (central processing unit) with some memory, basic
arithmetic capabilities and user input/output. The memory contains 128 words,
each word having 13 bit. This limits the integers to the range -4096 to 4095. A
memory cell can either contain some data or a command, though at runtime you
cannot tell the difference between them, as data and commands are represented
just the same. Thus it might happen that you accidentally try to execute data
fragments or read code.

If the cell contains a command, then the first 6 bit describe the instruction
and the remaining 7 bit the operand (the "parameter" to the instruction). This
makes for 2^6 = 64 different instructions and operands from 0 to 127 (remember,
the memory has a size of 128).

.. _the short DC manual: http://oberstufeninformatik.de/dc/DCKurz.pdf

Register
--------

The registers are used by the CPU for internal temporary storage of values,
calculation purposes or execution control

Instruction register (IR)
^^^^^^^^^^^^^^^^^^^^^^^^^

Before a command can be executed, it has to be loaded into the instruction
register. Thus this register has a size of 13 bits. The control unit then
seperates the command into the 6 bit instruction and the 7 bit operand. You can
see this seperation by the whitespace in the visualization area. The control
then executes the instruction, which is saved internally.

Program counter (PC)
^^^^^^^^^^^^^^^^^^^^

The program counter contains the cell of the next command. Every cycle it will
get incremented by one. A jump instruction also modifies this register and sets
its value to the jump destination.

You can modify this register directly using the command line.

Address register (AR)
^^^^^^^^^^^^^^^^^^^^^

This register contains the memory address of the memory cell that you want to
read or write to. You cannot manipulate it directly, the control unit will take
care of setting the AR to the right value.

Data register (DR)
^^^^^^^^^^^^^^^^^^

The data register contains the data that you want to read or write to the
memory, just like the address register contains the address.

Accumulator (AC)
^^^^^^^^^^^^^^^^

The accumulator is the central register in the microprocessor. Together with the
arithmetic logical unit (ALU) it is responsible for the actual calculations. For
example you can add a value of the RAM to the accumulator, the accumulator then
contains the result of the addition. With the accumulator in DC, you can add,
subtract, negate, increment by one and decrement by one (no division or
multiplication available). In reality, there are usually more than one register
of this kind.

Stack pointer (SP)
^^^^^^^^^^^^^^^^^^

At first the stack pointer points to the cell 127 (last cell). When you push a
value to the stack, the stack pointer gets decremented by one. Thus the stack
pointer always points to the next free memory cell below the stack. The stack
grows "down", starting at the last cell 127.

When you cann a subroutine the return address is automatically pushed onto the
stack. That way you can return from the subroutine, no matter from where you
called it.

The stack is also used for function parameters and return values.

Base pointer (BP)
^^^^^^^^^^^^^^^^^

The base pointer is like a second stack pointer. Unlike the stack pointer it
doesn't automatically get decreased if you push values, thus addressing local
variables is a lot easier using a constant value (the base pointer) instead of a
changing one (the stack pointer). You can transfer values between the stack
pointer and the base pointer.

Data transport
--------------

Data transport between the various hardware parts works with the bus. Some of
the bus connections are represented by white lines in the visualization window.

Address bus
^^^^^^^^^^^

The address bus can transmit the address of a memory cell, thus it needs a width
of 7 bit to address all 128 memory cells. In real computers however, the bus
usually has a size of 8 bit, 16 bit (both deprecated), 20 bit, 24 bit, 32 bit or
64 bit.

Data bus
^^^^^^^^

The data bus can transfer data between the registers and the memory. In this
model it has a width of 13 bit, though in reality bus widths of 8/16/32/64 bit
are common.

Control wires
^^^^^^^^^^^^^

Some additional connections are required, for example to indicate if you want to
read from or write to the RAM. Those wires are not displayed.

Instruction set
---------------

This is the most important part if you want to program the DC: the list of
supported instructions. The table contains the mnemonic and the
description. Note that some of the instructions may need an operand (such as
``LDA``) while others don't (such as ``INC``).

Basic instructions
^^^^^^^^^^^^^^^^^^

+---------+--------------------------------------------------------------------+
| LDA     | LOAD INTO ACCUMULATOR - Load the value of the given cell into the  |
|         | accumulator                                                        |
+---------+--------------------------------------------------------------------+
| STA     | STORE ACCUMULATOR TO MEMORY - Store the value of the accumulator   |
|         | to the given memory cell                                           |
+---------+--------------------------------------------------------------------+
| ADD     | ADD TO ACCUMULATOR - Add the value of the given cell to the        |
|         | accumulator                                                        |
+---------+--------------------------------------------------------------------+
| SUB     | SUBTRACT FROM ACCUMULATOR - Subtract the value of the given cell   |
|         | from the accumulator                                               |
+---------+--------------------------------------------------------------------+
| NEG     | NEGATE ACCUMULATOR - Negate the value in the accumulator           |
+---------+--------------------------------------------------------------------+
| INC     | INCREMENT ACCUMULATOR - Increment the accumulator by one           |
+---------+--------------------------------------------------------------------+
| DEC     | DECREMENT ACCUMULATOR - Decrement the accumulator by one           |
+---------+--------------------------------------------------------------------+
| OUT     | OUTPUT MEMORY - Output the value of the given memory cell to the   |
|         | user                                                               |
+---------+--------------------------------------------------------------------+
| INM     | INPUT TO MEMORY - Read an integer value from the user and save it  |
|         | at the given memory cell                                           |
+---------+--------------------------------------------------------------------+
| END     | END - End the program                                              |
+---------+--------------------------------------------------------------------+
| DEF     | DEFINE WORD - Set the memory cell to the given value, e.g. if cell |
|         | 34 contains ``DEF 3141``, the value of 34 will be 3141. This is    |
|         | not really an instruction for the CPU but available to define cell |
|         | values in a program                                                |
+---------+--------------------------------------------------------------------+

Jump instructions
^^^^^^^^^^^^^^^^^

+---------+--------------------------------------------------------------------+
| JMP     | JUMP - Unconditionally jump to the given cell and resume execution |
+---------+--------------------------------------------------------------------+
| JMS     | JUMP IF MINUS - Jump only if accumulator < 0                       |
+---------+--------------------------------------------------------------------+
| JPL     | JUMP IF PLUS - Jump only if accumulator > 0                        |
+---------+--------------------------------------------------------------------+
| JZE     | JUMP IF ZERO - Jump only if accumulator = 0                        |
+---------+--------------------------------------------------------------------+
| JNM     | JUMP IF NOT MINUS - Jump only if accumulator >= 0                  |
+---------+--------------------------------------------------------------------+
| JNP     | JUMP IF NOT PLUS - Jump only if accumulator <= 0                   |
+---------+--------------------------------------------------------------------+
| JNZ     | JUMP IF NOT ZERO - Jump only if accumulator != 0                   |
+---------+--------------------------------------------------------------------+
| JSR     | JUMP TO SUBROUTINE - Jump to the given subroutine. The return      |
|         | address is automatically pushed to the stack.                      |
+---------+--------------------------------------------------------------------+
| RTN     | RETURN FROM SUBROUTINE - Jump back from a subroutine by taking a   |
|         | return address from the stack                                      |
+---------+--------------------------------------------------------------------+

Stack operations (using SP)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

+---------+--------------------------------------------------------------------+
| PSH     | PUSH ACCUMULATOR TO STACK - Push the value of the accumulator onto |
|         | the stack                                                          |
+---------+--------------------------------------------------------------------+
| POP     | POP FROM STACK TO ACCUMULATOR - Pop a value from the stack into    |
|         | the accumulator                                                    |
+---------+--------------------------------------------------------------------+
| PSHM    | PUSH MEMORY TO STACK - Push the value of the given memory cell     |
|         | onto the stack                                                     |
+---------+--------------------------------------------------------------------+
| POPM    | POP FROM STACK TO MEMORY - Pop a value from the stack into the     |
|         | given memory cell                                                  |
+---------+--------------------------------------------------------------------+
| LDAS    | LOAD FROM STACK TO ACCUMULATOR - Load the value at cell SP+XXX     |
|         | into the accumulator, XXX is given as operand.                     |
+---------+--------------------------------------------------------------------+
| STAS    | STORE ACCUMULATOR TO STACK - Store the value of the accumulator to |
|         | the cell SP+XXX                                                    |
+---------+--------------------------------------------------------------------+
| ADDS    | ADD STACK TO ACCUMULATOR - Adds the value of SP+XXX to the         |
|         | accumulator                                                        |
+---------+--------------------------------------------------------------------+
| SUBS    | SUBTRACT STACK FROM ACCUMULATOR - Subtract the value of SP+XXX     |
|         | from the accumulator                                               |
+---------+--------------------------------------------------------------------+
| OUTS    | OUT STACK - Output the value of the cell at SP+XXX                 |
+---------+--------------------------------------------------------------------+
| INS     | INPUT TO STACK - Read an user value to the cell at SP+XXX          |
+---------+--------------------------------------------------------------------+

Stack operations (using BP)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

+---------+--------------------------------------------------------------------+
| LDAB    | LOAD FROM STACK TO ACCUMULATOR - Load the value at cell BP+XXX     |
|         | into the accumulator, XXX is given as operand.                     |
+---------+--------------------------------------------------------------------+
| STAB    | STORE ACCUMULATOR TO STACK - Store the value of the accumulator to |
|         | the cell BP+XXX                                                    |
+---------+--------------------------------------------------------------------+
| ADDB    | ADD STACK TO ACCUMULATOR - Adds the value of BP+XXX to the         |
|         | accumulator                                                        |
+---------+--------------------------------------------------------------------+
| SUBB    | SUBTRACT STACK FROM ACCUMULATOR - Subtract the value of BP+XXX     |
|         | from the accumulator                                               |
+---------+--------------------------------------------------------------------+
| OUTB    | OUT STACK - Output the value of the cell at BP+XXX                 |
+---------+--------------------------------------------------------------------+
| INB     | INPUT TO STACK - Read an user value to the cell at BP+XXX          |
+---------+--------------------------------------------------------------------+
| SPBP    | TRANSFER SP TO BP - Set the value of SP to the register BP         |
+---------+--------------------------------------------------------------------+
| BPSP    | TRANSFER BP TO SP - Set the value of BP to the register SP         |
+---------+--------------------------------------------------------------------+
| POPB    | POP BP - Take a value from the stack and put it into BP            |
+---------+--------------------------------------------------------------------+
| PSHB    | PUSH BP - Put the value of BP onto the stack                       |
+---------+--------------------------------------------------------------------+
