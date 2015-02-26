#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# pylint: disable=too-few-public-methods
"""
Main module of the DC
"""
from .parts import Register, RAM
from .errors import (NoInputValue, ScriptError, AssembleError, Overflow,
                     InvalidAddress, DCError)
from .util import IDict


class DCConfig():
    """
    A (very small) class containing some configuration variables like
    the addresswidth. Maybe this will be expanded later
    """
    def __init__(self):
        self.addrwidth = 7
        self.controlbits = 6


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
    getInput and showOutput functions.
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

    def __init__(self, config):
        """
        Set up a DC with the given config
        """
        self.conf = config
        aw, cb = config.addrwidth, config.controlbits
        self.cellwidth = aw + cb
        self.maddr = 2 ** config.addrwidth - 1
        self.mcontr = 2 ** config.controlbits - 1
        self.maxint = 2 ** (self.cellwidth - 1) - 1
        self.minint = 2 ** (self.cellwidth - 1) * -1
        self.ram = RAM(2 ** config.addrwidth)

        self.ir = Register("IR", aw + cb)
        self.dr = Register("DR", aw + cb)
        self.pc = Register("PC", aw)
        self.ac = Register("AC", aw + cb)
        self.ar = Register("AR", aw)
        self.sp = Register("SP", aw, self.maddr)
        self.bp = Register("BP", aw, self.maddr)

        # A collection of addresses pushed onto the stack by JSR so we
        # can color them differently.
        self.retaddrs = set()

        self.interface = None
        self.running = False

    def reset(self):
        """
        Reset the DC to its initial state
        """
        self.ir.set(0)
        self.dr.set(0)
        self.pc.set(0)
        self.ac.set(0)
        self.ar.set(0)
        self.sp.set(self.maddr)
        self.bp.set(self.maddr)
        self.retaddrs = set()
        self.running = False
        self.ram.clear()

    def getcmd(self, value):
        """
        Return the name of the command for the given cell value
        """
        opc = value >> self.conf.addrwidth
        mn = self.mnemo.get(opc, "DEF")
        return mn

    def parsecmd(self, line):
        """
        Parse a string representation of a command ("CMD ARG") into an
        integer value. Instead of giving the string representation, you
        can provide an already splitted list too.

        >>> parsecmd("JMP 127") == 0b0001001111111
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
                if full > self.maxint or full < self.minint:
                    raise ScriptError("{} <= x <= {}".format(self.maxint,
                                                             self.minint))
            except ValueError:
                raise ScriptError("Not a valid integer: {}".format(line[1]))
        else:
            try:
                cmd = self.opcodes[line[0].upper()]
            except KeyError:
                raise ScriptError("Invalid instruction: {}".format(line[0]))
            cmd <<= self.conf.addrwidth
            try:
                target = int(line[1])
                if target > self.maddr:
                    raise InvalidAddress(
                        "The max value is {}".format(self.maddr))
            except ValueError:
                raise InvalidAddress("Not a valid address: {}".format(line[1]))
            else:
                full = cmd | target

        return full & (2 ** self.cellwidth - 1)

    @staticmethod
    def nocomment(line, cchar=";"):
        """
        Strip of a comment when the comment char is cchar
        """
        index = line.find(cchar)
        if index == -1:
            return line
        else:
            return line[:index]

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
        v = IDict()
        t = []
        no = 0
        # Part one: get lines and local variables
        for lno, line in enumerate(cls.nocomment(l) for l in lines):
            # Switch from zero based index to one based index (human
            # index):
            lno += 1
            line = line.strip()
            if not line:
                continue
            line = line.split()
            l = None
            while line:
                token = line.pop(0)
                if token.upper() in cls.opcodes or token.upper() == "DEF":
                    # command
                    if line:
                        t.append([lno, token, line.pop(0)])
                    else:
                        t.append([lno, token])
                    no += 1
                    l = None
                    continue
                elif token.upper() == "EQUAL":
                    if l in v:
                        raise AssembleError(
                            "Variable {} already assigned (line {})"
                            .format(l, lno))
                    v[l] = int(line.pop(0))
                    break
                else:
                    token = token.rstrip(":")
                    # skip if the next token is EQUAL, e.g. the line is
                    # baum EQUAL 1
                    # otherwise it will lead to errors due to multiple labels
                    # with the same name
                    if line and line[0].upper() == "EQUAL":
                        l = token
                        continue
                    if token in v:
                        raise AssembleError(
                            "Label {} already defined (line {})"
                            .format(token, lno))
                    v[token] = no
                l = token

        # Part two: glue everything together, strip out labels, replace them
        # with the numbers from part one
        res = []
        for no, token in enumerate(t):
            if len(token) == 3:
                # Apparently, JMP done: is just as valid as JMP done
                # so strip off the colon
                adr = token[2].strip(": \r\n")
                if adr in v:
                    adr = v[adr]
                else:
                    try:
                        adr = int(adr)
                    except ValueError:
                        raise AssembleError(
                            "Invalid address: {} (line {})"
                            .format(adr, token[0]))
                res.append("{} {} {}".format(no, token[1], adr))
            else:
                res.append("{} {}".format(no, token[1]))
        return res

    def load(self, lines, clear=True):
        """
        Load a file. The file is given as a list of its lines (like the
        return value of .assemble()). If clear is True, the DC will be
        resetted to its initial state before loading the file.
        Otherwise the file just updates the current content of the RAM.
        """
        if clear:
            self.reset()
        for no, line in enumerate(self.nocomment(l) for l in lines):
            # compatibility bit, I don't know what this character is
            # for. It's there for files produced by the original
            # version of DC:
            if line == "\x1a":
                continue
            # Switch from zero-based indexing to one-based indexing
            # (human indexes)
            no += 1
            line = line.strip()
            if not line:
                continue
            line = line.split()
            if len(line) < 2 or len(line) > 3:
                raise ScriptError(
                    "Invalid line {}: {}"
                    .format(no, " ".join(line)))
            try:
                addr = int(line[0])
                if addr > self.maddr or addr < 0:
                    raise ScriptError(
                        "{} is outside of the available memory (line {})"
                        .format(addr, no))
            except ValueError:
                raise ScriptError(
                    "Not a valid address: {} (line {})"
                    .format(line[0], no))
            try:
                full = self.parsecmd(line[1:])
            except DCError as de:
                de.msg += " (line {})".format(no)
                raise de
            self.ram[addr] = full

    def getmem(self):
        """
        Copy the data from the memory cell currently pointed at by the
        address register (AR) into the data register (DR)
        """
        data = self.ram[self.ar.value]
        self.dr.set(data)

    def savemem(self):
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
        self.running = True
        while self.running:
            self.cycle()

    def cycle(self):
        """
        Execute a single instruction. This is done in the von Neumann
        style
        """
        # Step 1: Fetch
        self.pc.to(self.ar)
        self.getmem()
        self.dr.to(self.ir)
        # Step 2: Decode
        self.pc.inc()
        cmd = self.ir.value >> (self.conf.addrwidth)
        adr = self.ir.value & self.maddr
        # Step 3: Fetch operands
        self.ar.set(adr)
        self.getmem()
        try:
            f = self.mnemo[cmd]
        except KeyError:
            # DEF
            return
        # Step 4: Execute
        f = getattr(self, f)
        f()
        # Step 5 (write back) is done in f

    def LDA(self):
        self.dr.to(self.ac)

    def STA(self):
        self.ac.to(self.dr)
        self.savemem()

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
        self.savemem()
        self.retaddrs.add(self.sp.value)
        self.sp.dec()
        self.pc.set(self.ir.value & self.maddr)

    def RTN(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.getmem()
        try:
            self.retaddrs.remove(self.sp.value)
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
        self.savemem()

    def POP(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.getmem()
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
        self.interface.showOutput(self.dr.signed_value)

    def INM(self):
        try:
            value = self.interface.getInput()
        except NoInputValue:
            self.running = False
            return
        self.dr.set(value)
        self.savemem()

    def END(self):
        self.running = False

    def PSHM(self):
        self.sp.to(self.ar)
        self.savemem()
        self.sp.dec()

    def POPM(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.getmem()
        self.ir.to(self.ar)
        self.savemem()

    def LDAS(self):
        if self.sp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.dr.to(self.ac)

    def STAS(self):
        if self.sp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.ac.to(self.dr)
        self.savemem()

    def ADDS(self):
        if self.sp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUBS(self):
        if self.sp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
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
        self.getmem()
        self.dr.to(self.bp)

    def PSHB(self):
        self.bp.to(self.dr)
        self.sp.to(self.ar)
        self.savemem()
        self.sp.dec()

    def LDAB(self):
        if self.bp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.dr.to(self.ac)

    def STAB(self):
        if self.bp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.ac.to(self.dr)
        self.savemem()

    def ADDB(self):
        if self.bp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUBB(self):
        if self.bp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        if self.ac.will_overflow(self.ac.signed_value - self.dr.signed_value):
            raise Overflow
        self.ac -= self.dr

    def OUTS(self):
        if self.sp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.interface.showOutput(self.dr.signed_value)

    def OUTB(self):
        if self.bp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.interface.showOutput(self.dr.signed_value)

    def INS(self):
        if self.sp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        value = self.interface.getInput()
        self.dr.set(value)
        self.savemem()

    def INB(self):
        if self.bp.value + (self.ir.value & self.maddr) > self.maddr:
            raise InvalidAddress
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        value = self.interface.getInput()
        self.dr.set(value)
        self.savemem()
