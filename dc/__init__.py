#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# pylint: disable=too-few-public-methods
"""
Main module of the DC
"""
from .parts import Register, RAM
from .errors import (NoInputValue, ScriptError, AssembleError, Overflow,
                     InvalidAddress, DCError, Breakpoint)
from collections import namedtuple


Token = namedtuple("Token", ["token", "line_number"])
Instruction = namedtuple("Instruction", ["number", "opcode", "arg",
                                         "source_line"])


class DCConfig():
    """
    A (very small) class containing some configuration variables like
    the addresswidth. Maybe this will be expanded later
    """
    def __init__(self):
        self.address_width = 7
        self.control_bits = 6


class DC():
    # The following are probably okay to disable here, since every assembly
    # command is a (public) function without docstring. (maybe make those
    # "private" instead?)
    # pylint: disable=too-many-instance-attributes,too-many-public-methods
    # pylint: disable=invalid-name,missing-docstring
    """
    Main class for the DC. This class provides all operations that are
    independent from the interface. It can be used to simulate a DC
    even without the GUI as long as you provide a mock interface with
    get_input and show_output functions.
    """
    # Mapping NAME - CODE
    # DEF is ------
    opcodes = {
        "LDA": 0b000000,  # LoaD Accumulator LDA adr
        "STA": 0b000001,  # STore Accumulator STA adr
        "ADD": 0b000010,  # ADD memory to accu ADD adr
        "SUB": 0b000011,  # SUBtract memory SUB adr
        "JMP": 0b000100,  # JuMP JMP adr
        "JMS": 0b000101,  # Jump if MinuS JMS adr
        "JPL": 0b001000,  # Jump if PLus JPL adr
        "JZE": 0b001001,  # Jump if ZEro JZE adr
        "JNM": 0b011010,  # Jump if Not Minus JNM adr
        "JNP": 0b011011,  # Jump if Not Plus JNP adr
        "JNZ": 0b010100,  # Jump if Not Zero JNZ adr
        "JSR": 0b000110,  # Jump to SubRoutine JSR adr
        "RTN": 0b000111,  # ReTurN RTN
        "PSH": 0b001100,  # PuSH accu PSH
        "POP": 0b001101,  # POP into accu POP
        "PSHM": 0b001110,  # PuSH Memory PSHM adr
        "POPM": 0b001111,  # POP into Memory POPM adr
        "LDAS": 0b010101,  # LoaD Accu from Sp + x LDAS x
        "STAS": 0b010110,  # STore Accu to Sp + x STAS x
        "ADDS": 0b010111,  # ADD Sp+x to accu ADDS x
        "SUBS": 0b011000,  # SUBtract SP+x from accu SUBS x
        "SPBP": 0b100111,  # transfer SP to BP
        "BPSP": 0b100110,  # transfer BP to SP
        "POPB": 0b100100,  # POP Bp
        "PSHB": 0b100101,  # PuSH Bp
        "LDAB": 0b011110,  # LoaD accu from Bp + x LDAB x
        "STAB": 0b011111,  # Store accu to Bp + x STAB x
        "ADDB": 0b100000,  # ADD Bp + x to accu ADDB x
        "SUBB": 0b100001,  # SUBtract Bp+x from accu SUBB x
        "NOP": 0b010000,  # No OPeration NOP
        "NEG": 0b010001,  # NEGate accu NEG
        "INC": 0b010010,  # INCrement accu INC
        "DEC": 0b010011,  # DECrement accu DEC
        "OUT": 0b001010,  # OUTput memory OUT adr
        "OUTS": 0b011001,  # OUT Sp + x OUTS x
        "OUTB": 0b100010,  # OUT Bp + x OUTB x
        "INM": 0b011100,  # INput to Memory INM adr
        "INS": 0b011101,  # INput to Sp + x INS x
        "INB": 0b100011,  # INput to Bp + x INB x
        "END": 0b001011
    }
    # Mapping CODE - NAME
    mnemo = dict((val, key) for key, val in opcodes.items())

    opcodes_without_arg = {
        "RTN", "PSH", "POP", "SPBP", "BPSP", "POPB", "PSHB", "NOP", "NEG",
        "INC", "DEC", "END",
    }

    def __init__(self, config):
        """
        Set up a DC with the given config
        """
        self.conf = config
        self.cellwidth = config.address_width + config.control_bits
        self.max_address = 2 ** config.address_width - 1
        self.max_int = 2 ** (self.cellwidth - 1) - 1
        self.min_int = 2 ** (self.cellwidth - 1) * -1
        self.ram = RAM(2 ** config.address_width)

        self.ir = Register("IR", config.address_width + config.control_bits)
        self.dr = Register("DR", config.address_width + config.control_bits)
        self.pc = Register("PC", config.address_width)
        self.ac = Register("AC", config.address_width + config.control_bits)
        self.ar = Register("AR", config.address_width)
        self.sp = Register("SP", config.address_width, self.max_address)
        self.bp = Register("BP", config.address_width, self.max_address)

        # A collection of addresses pushed onto the stack by JSR so we
        # can color them differently.
        self.return_addresses = set()

        self.breakpoints = set()

        self.interface = None
        self.is_running = False

    def reset(self):
        """
        Reset the DC to its initial state
        """
        self.ir.set(0)
        self.dr.set(0)
        self.pc.set(0)
        self.ac.set(0)
        self.ar.set(0)
        self.sp.set(self.max_address)
        self.bp.set(self.max_address)
        self.return_addresses = set()
        self.breakpoints = set()
        self.is_running = False
        self.ram.clear()

    def command_name(self, value):
        """
        Return the name of the command for the given cell value
        """
        opc = value >> self.conf.address_width
        mn = self.mnemo.get(opc, "DEF")
        return mn

    def parse_command(self, line):
        """
        Parse a string representation of a command ("CMD ARG") into an
        integer value. Instead of giving the string representation, you
        can provide an already splitted list too.

        >>> parse_command("JMP 127") == 0b0001001111111
        True
        """
        try:
            line = line.split()
        except AttributeError:
            pass
        if len(line) == 1:
            line.append(0)
        cmd = line[0].upper()
        if cmd == "DEF":
            try:
                full = int(line[1])
                if full > self.max_int or full < self.min_int:
                    raise ScriptError("{} <= x <= {}".format(self.max_int,
                                                             self.min_int))
            except ValueError:
                raise ScriptError("Not a valid integer: {}".format(line[1]))
        else:
            try:
                cmd = self.opcodes[line[0].upper()]
            except KeyError:
                raise ScriptError("Invalid instruction: {}".format(line[0]))
            cmd <<= self.conf.address_width
            try:
                target = int(line[1])
                if target > self.max_address:
                    raise InvalidAddress(
                        "The max value is {}".format(self.max_address))
            except ValueError:
                raise InvalidAddress("Not a valid address: {}".format(line[1]))
            else:
                full = cmd | target

        return full & (2 ** self.cellwidth - 1)

    @staticmethod
    def strip_comment(line, comment_delim=";"):
        """
        Strip of a comment with the given comment delimiter
        """
        index = line.find(comment_delim)
        if index == -1:
            return line
        else:
            return line[:index]

    @staticmethod
    def tokenize(lines):
        """
        Create a stream of tokens created by splitting the input lines.
        Returns a generator of Token-objects, recording both the token and the
        line number in the source.

        >>> list(tokenize(["Castles In", "The Air"]))
        [Token(token='Castles', line_number=1),
        Token(token='In', line_number=1),
        Token(token='The', line_number=2),
        Token(token='Air', line_number=2)]
        """
        # We start counting the lines with 1 as humans would do
        for line_number, line in enumerate(lines, 1):
            line = DC.strip_comment(line)
            line = line.strip()
            tokens = line.split()
            tokens = (token.strip(":") for token in tokens)
            yield from (Token(token, line_number) for token in tokens if token)

    @classmethod
    def assemble(cls, lines):
        # pylint: disable=too-many-branches
        """
        Assemble a DCL file to a DC file so that it can be loaded.
        The file is given as a list of its lines and the DC file is
        returned as a list of lines.

        >>> assemble(["INM 20", "OUT 20"])
        ["0 INM 20", "1 OUT 20"]
        """
        labels = {}
        # Needed to keep track of all possible labels since this is permitted:
        # ALPHA
        # BETA
        # GAMMA DEF 20
        # now ALPHA BETA and GAMMA will all point to DEF 20
        future_labels = []
        instruction_number = 0
        tokens = cls.tokenize(lines)
        program = []
        for token_obj in tokens:
            token = token_obj.token.upper()
            if token == "EQUAL":
                if not future_labels:
                    # line_number is the "human readable" line number, but the
                    # error expects 0-based indexes
                    raise AssembleError("Expected label (line {})"
                                        .format(token_obj.line_number),
                                        token_obj.line_number - 1)
                # EQUAL only takes the label directly in front of it
                label = future_labels.pop()
                try:
                    value = next(tokens).token
                except StopIteration:
                    raise AssembleError("Expected value (line {})"
                                        .format(token_obj.line_number),
                                        token_obj.line_number - 1)
                if label in labels:
                    raise AssembleError("Label {} already defined (line {})"
                                        .format(label, token_obj.line_number),
                                        token_obj.line_number - 1)
                labels[label] = value
            elif token in cls.opcodes or token == "DEF":
                if token in cls.opcodes_without_arg:
                    arg = None
                else:
                    try:
                        arg = next(tokens).token.upper()
                    except StopIteration:
                        raise AssembleError("Expected argument (line {})"
                                            .format(token_obj.line_number),
                                            token_obj.line_number - 1)
                program.append(Instruction(instruction_number, token, arg,
                                           token_obj.line_number))
                # Every label that came before this instruction will now point
                # at this instruction
                for label in future_labels:
                    if label in labels:
                        raise AssembleError("Label {} already defined "
                                            "(line {})".format(
                                                label, token_obj.line_number),
                                            token_obj.line_number - 1)
                    labels[label] = instruction_number
                future_labels.clear()
                instruction_number += 1
            # Everything that is not a valid instruction is treated as a
            # potential label
            else:
                future_labels.append(token)

        result = []
        for instruction in program:
            if instruction.arg is None:
                result.append("{} {}".format(instruction.number,
                                             instruction.opcode))
                continue
            arg = labels.get(instruction.arg)
            if arg is None:
                try:
                    # We need this for stuff like DEF 20, otherwise we'd get
                    # the error "Invalid label" for 20. Note that this allows
                    # the following program to work even though it doesn't work
                    # in the original DC:
                    # INM 20
                    # LDA 20
                    # The way we do it is probably easier than keeping track of
                    # every instruction that takes a numeric argument instead
                    # of a label.
                    arg = int(instruction.arg)
                except ValueError:
                    raise AssembleError("Invalid label (line {})"
                                        .format(instruction.source_line),
                                        instruction.source_line - 1)
            result.append("{} {} {}".format(instruction.number,
                                            instruction.opcode, arg))
        return result

    def load(self, lines, clear=True):
        """
        Load a file. The file is given as a list of its lines (like the
        return value of .assemble()). If clear is True, the DC will be
        resetted to its initial state before loading the file.
        Otherwise the file just updates the current content of the RAM.
        """
        if clear:
            self.reset()
        lines = map(self.strip_comment, lines)
        # line_number is the "human indexed" line number, this is good for
        # showing but means that we need to use (line_number - 1) when passing
        # it to ScriptError so the correct line is highlighted later, since the
        # errors expect 0-based indexes
        for line_number, line in enumerate(lines, 1):
            # compatibility bit, I don't know what this character is
            # for. It's there for files produced by the original
            # version of DC:
            if line == "\x1a":
                continue
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2 or len(parts) > 3:
                raise ScriptError("Invalid line {}: {}"
                                  .format(line_number, line), line_number - 1)
            try:
                address = int(parts[0])
                if address > self.max_address or address < 0:
                    raise InvalidAddress("{} is outside of the available memor"
                                         "y (line {})".format(address,
                                                              line_number),
                                         line_number - 1)
            except ValueError:
                raise InvalidAddress("Not a valid address: {} (line {})"
                                     .format(parts[0], line_number),
                                     line_number - 1)
            try:
                full = self.parse_command(parts[1:])
            except DCError as error:
                error.msg += " (line {})".format(line_number)
                error.line_number = line_number - 1
                raise error
            self.ram[address] = full

    def get_memory(self):
        """
        Copy the data from the memory cell currently pointed at by the
        address register (AR) into the data register (DR)
        """
        data = self.ram[self.ar.value]
        self.dr.set(data)

    def save_memory(self):
        """
        Copy the data from the data register (DR) to the memory cell
        currently pointed at by the address register (AR)
        """
        self.ram[self.ar.value] = self.dr.value

    def run(self):
        """
        Execute the whole program until an END is reached or an error
        occurs
        """
        self.is_running = True
        while self.is_running:
            self.cycle()

    def cycle(self):
        """
        Execute a single instruction. This is done in the von Neumann
        style
        """
        # Step 1: Fetch
        self.pc.to(self.ar)
        self.get_memory()
        self.dr.to(self.ir)
        # Step 2: Decode
        self.pc.inc()
        cmd = self.ir.value >> (self.conf.address_width)
        adr = self.ir.value & self.max_address
        # Step 3: Fetch operands
        self.ar.set(adr)
        self.get_memory()
        try:
            f = self.mnemo[cmd]
        except KeyError:
            # DEF
            return
        # Step 4: Execute
        f = getattr(self, f)
        f()
        # Step 5 (write back) is done in f

        # We detect the breakpoint the command BEFORE reaching the
        # breakpoint, otherwise starting from a breakpoint'ed point
        # would be awkward. But it would also be stupid to break if
        # the current command is END and the breakpoint would never be
        # reached, so we need to check that too
        if self.is_running and self.pc.value in self.breakpoints:
            self.is_running = False
            raise Breakpoint("Breakpoint for {} set".format(self.pc.value))

    def LDA(self):
        self.dr.to(self.ac)

    def STA(self):
        self.ac.to(self.dr)
        self.save_memory()

    def ADD(self):
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUB(self):
        if self.ac.will_overflow(self.ac.signed_value - self.dr.signed_value):
            raise Overflow
        self.ac -= self.dr

    def JMP(self):
        self.ar.to(self.pc)

    def JMS(self):
        if self.ac.leftmost == 1:
            self.ar.to(self.pc)

    def JPL(self):
        if self.ac.signed_value > 0:
            self.ar.to(self.pc)

    def JZE(self):
        if self.ac.signed_value == 0:
            self.ar.to(self.pc)

    def JNM(self):
        if self.ac.leftmost == 0:
            self.ar.to(self.pc)

    def JNP(self):
        if self.ac.leftmost == 1 or self.ac.value == 0:
            self.ar.to(self.pc)

    def JNZ(self):
        if self.ac.signed_value != 0:
            self.ar.to(self.pc)

    def JSR(self):
        self.pc.to(self.dr)
        self.sp.to(self.ar)
        self.save_memory()
        self.return_addresses.add(self.sp.value)
        self.sp.dec()
        self.pc.set(self.ir.value & self.max_address)

    def RTN(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.get_memory()
        try:
            self.return_addresses.remove(self.sp.value)
        except KeyError:
            # Bad coded DC program, ignore it (RTN while SP was wrong)
            # the user will probably have to worry about a non-working
            # DC program anway, so don't cease to work now and just be
            # nice :)
            pass
        self.dr.to(self.pc)

    def PSH(self):
        self.sp.to(self.ar)
        self.sp.dec()
        self.ac.to(self.dr)
        self.save_memory()

    def POP(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.get_memory()
        self.dr.to(self.ac)

    def NOP(self):
        pass

    def NEG(self):
        self.ac.neg()

    def INC(self):
        if self.ac.will_overflow(self.ac.signed_value + 1):
            raise Overflow
        self.ac.inc()

    def DEC(self):
        if self.ac.will_overflow(self.ac.signed_value - 1):
            raise Overflow
        self.ac.dec()

    def OUT(self):
        self.interface.show_output(self.dr.signed_value)

    def INM(self):
        try:
            value = self.interface.get_input()
        except NoInputValue:
            self.is_running = False
            return
        self.dr.set(value)
        self.save_memory()

    def END(self):
        self.is_running = False

    def PSHM(self):
        self.sp.to(self.ar)
        self.save_memory()
        self.sp.dec()

    def POPM(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.get_memory()
        self.ir.to(self.ar)
        self.save_memory()

    def LDAS(self):
        address = self.sp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        self.dr.to(self.ac)

    def STAS(self):
        address = self.sp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.ac.to(self.dr)
        self.save_memory()

    def ADDS(self):
        address = self.sp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUBS(self):
        address = self.sp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        if self.ac.will_overflow(self.ac.signed_value - self.dr.signed_value):
            raise Overflow
        self.ac -= self.dr

    def SPBP(self):
        self.sp.to(self.bp)

    def BPSP(self):
        self.bp.to(self.sp)

    def POPB(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.get_memory()
        self.dr.to(self.bp)

    def PSHB(self):
        self.bp.to(self.dr)
        self.sp.to(self.ar)
        self.save_memory()
        self.sp.dec()

    def LDAB(self):
        address = self.bp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        self.dr.to(self.ac)

    def STAB(self):
        address = self.bp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.ac.to(self.dr)
        self.save_memory()

    def ADDB(self):
        address = self.bp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUBB(self):
        address = self.bp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        if self.ac.will_overflow(self.ac.signed_value - self.dr.signed_value):
            raise Overflow
        self.ac -= self.dr

    def OUTS(self):
        address = self.sp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        self.interface.show_output(self.dr.signed_value)

    def OUTB(self):
        address = self.bp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        self.get_memory()
        self.interface.show_output(self.dr.signed_value)

    def INS(self):
        address = self.sp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        value = self.interface.get_input()
        self.dr.set(value)
        self.save_memory()

    def INB(self):
        address = self.bp.value + (self.ir.value & self.max_address)
        if address > self.max_address:
            raise InvalidAddress
        self.ar.set(address)
        value = self.interface.get_input()
        self.dr.set(value)
        self.save_memory()
