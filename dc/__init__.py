#!/usr/bin/python3

from dc.parts import Register, RAM
from dc.errors import NoInputValue, ScriptError, AssembleError, Overflow
from threading import RLock

class DCConfig():
    def __init__(self):
        self.addrwidth = 7
        self.controlbits = 6

class DC():
    """Main class for the DC"""
    # DEF is ------
    opcodes = {
        "LDA": 0b000000, # LoaD Accumulator LDA adr
        "STA": 0b000001, # STore Accumulator STA adr
        "ADD": 0b000010, # ADD memory to accu ADD adr
        "SUB": 0b000011, # SUBtract memory SUB adr
        "JMP": 0b000100, # JuMP JMP adr
        "JMS": 0b000101, # Jump if MinuS JMS adr
        "JPL": 0b001000, # Jump if PLus JPL adr
        "JZE": 0b001001, # Jump if ZEro JZE adr
        "JNM": 0b011010, # Jump if Not Minus JNM adr
        "JNP": 0b011011, # Jump if Not Plus JNP adr
        "JNZ": 0b010100, # Jump if Not Zero JNZ adr
        "JSR": 0b000110, # Jump to SubRoutine JSR adr
        "RTN": 0b000111, # ReTurN RTN
        "PSH": 0b001100, # PuSH accu PSH
        "POP": 0b001101, # POP into accu POP
        "PSHM": 0b001110, # PuSH Memory PSHM adr
        "POPM": 0b001111, # POP into Memory POPM adr
        "LDAS": 0b010101, # LoaD Accu from Sp + x LDAS x
        "STAS": 0b010110, # STore Accu to Sp + x STAS x
        "ADDS": 0b010111, # ADD Sp+x to accu ADDS x
        "SUBS": 0b011000, # SUBtract SP+x from accu SUBS x
        "SPBP": 0b100111, # transfer SP to BP
        "BPSP": 0b100110, # transfer BP to SP
        "POPB": 0b100100, # POP Bp
        "PSHB": 0b100101, # PuSH Bp
        "LDAB": 0b011110, # LoaD accu from Bp + x LDAB x
        "STAB": 0b011111, # Store accu to Bp + x STAB x
        "ADDB": 0b100000, # ADD Bp + x to accu ADDB x
        "SUBB": 0b100001, # SUBtract Bp+x from accu SUBB x
        "NOP": 0b010000, # No OPeration NOP
        "NEG": 0b010001, # NEGate accu NEG
        "INC": 0b010010, # INCrement accu INC
        "DEC": 0b010011, # DECrement accu DEC
        "OUT": 0b001010, # OUTput memory OUT adr
        "OUTS": 0b011001, # OUT Sp + x OUTS x
        "OUTB": 0b100010, # OUT Bp + x OUTB x
        "INM": 0b011100, # INput to Memory INM adr
        "INS": 0b011101, # INput to Sp + x INS x
        "INB": 0b100011, # INput to Bp + x INB x
        "END": 0b001011
    }
    mnemo = dict((val, key) for key, val in opcodes.items())

    def __init__(self, config):
        self.conf = config
        aw, cb = config.addrwidth, config.controlbits
        self.cellwidth = aw + cb
        self.maddr = 2 ** config.addrwidth - 1
        self.mcontr = 2 ** config.controlbits - 1
        self.ram = RAM(2 ** config.addrwidth)

        self.ir = Register("IR", aw + cb)
        self.dr = Register("DR", aw + cb)
        self.pc = Register("PC", aw)
        self.ac = Register("AC", aw + cb)
        self.ar = Register("AR", aw)
        self.sp = Register("SP", aw, self.maddr)
        self.bp = Register("BP", aw, self.maddr)
        
        self.running = False

        self.interface = None
        self.lock = RLock()
    
    def reset(self):
        with self.lock:
            self.ir.set(0)
            self.dr.set(0)
            self.pc.set(0)
            self.ac.set(0)
            self.ar.set(0)
            self.sp.set(self.maddr)
            self.bp.set(self.maddr)
            self.running = False
            self.ram.clear()
    
    def getcmd(self, cell):
        opc = cell >> self.conf.addrwidth
        mn = self.mnemo.get(opc, "DEF")
        return mn

    def parsecmd(self, cmd):
        cmd = cmd.split()
        c = cmd.pop(0).upper()
        if c in self.opcodes:
            x = self.opcodes[c] << self.conf.addrwidth
            if cmd:
                try:
                    x |= int(cmd[0])
                except ValueError:
                    raise ScriptError("Invalid int: {}".format(cmd[0]))
        elif c == "DEF":
            try:
                x = int(cmd[0])
            except ValueError:
                raise ScriptError("Invalid int: {}".format(cmd[0]))
            except IndexError:
                raise ScriptError("DEF requires a parameter")
        else:
            raise ScriptError("Invalid instruction: {}".format(c))
        return x & (2**self.cellwidth - 1)
        
        
    @staticmethod
    def nocomment(line):
        index = line.find(";")
        if index == -1:
            return line
        else:
            return line[:index]

    @classmethod
    def assemble(cls, lines):
        v = {}
        t = []
        no = 0
        # Part one: get lines and local variables
        for lno, line in enumerate(cls.nocomment(l) for l in lines):
            line = line.strip()
            if not line:
                continue
            line = line.split()
            l = None
            while line:
                token = line.pop(0)
                if token.upper() in cls.opcodes or token.upper() == "DEF":
                    # command
                    t.append([token] + line)
                    no += 1
                    break
                elif token.upper() == "EQUAL":
                    if l in v:
                        raise AssembleError("Variable {} already assigned (line {})".format(l, lno))
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
                        raise AssembleError("Label {} already defined (line {})".format(token, lno))
                    v[token] = no
                l = token
        
        # Part two: glue everything together, strip out labels, replace them
        # with the numbers from part one
        res = []
        for no, token in enumerate(t):
            if len(token) == 2:
                adr = token[1]
                if adr in v:
                    adr = v[adr]
                else:
                    try:
                        adr = int(adr)
                    except ValueError:
                        raise AssembleError("Invalid address: {} (line {})".format(adr, no))
                res.append("{} {} {}".format(no, token[0], adr))
            else:
                res.append("{} {}".format(no, token[0]))
        return res

    def load(self, lines, clear=True):
        if clear:
            self.ram.clear()
        for no, line in enumerate(self.nocomment(l) for l in lines):
            # compatibility bit, idk what this character is for:
            if line == "\x1a":
                continue
            line = line.strip()
            if not line:
                continue
            line = line.split()
            if len(line) == 2:
                line.append(0)
            elif len(line) < 2 or len(line) > 3:
                raise ScriptError("Invalid line {}: {}".format(no, " ".join(line)))
            try:
                addr = int(line[0])
            except ValueError:
                raise ScriptError("Not a valid address: {} (line {})".format(line[0], no))
            cmd = line[1].upper()
            if cmd == "DEF":
                try:
                    full = int(line[2])
                except ValueError:
                    raise ScriptError("Not a valid integer: {} (line {})".format(line[2], no))
            else:
                try:
                    cmd = self.opcodes[line[1].upper()]
                except KeyError:
                    raise ScriptError("Invalid instruction: {} (line {})".format(line[1], no))
                cmd <<= self.conf.addrwidth
                try:
                    full = cmd | int(line[2])
                except ValueError:
                    raise ScriptError("Not a valid address: {} (line {})".format(line[2], no))
            with self.lock:
                self.ram[addr] = full

    def getmem(self):
        data = self.ram[self.ar.value]
        self.dr.set(data)

    def savemem(self):
        self.ram[self.ar.value] = self.dr.value
    
    def run(self):
        self.running = True
        while self.running:
            self.cycle()

    def cycle(self):
        with self.lock:
            self.pc.to(self.ar)
            self.getmem()
            self.dr.to(self.ir)
            cmd = self.ir.value >> (self.conf.addrwidth)
            adr = self.ir.value & self.maddr
            self.ar.set(adr)
            self.getmem()
            try:
                f = self.mnemo[cmd]
            except KeyError:
                # DEF
                self.pc.inc()
                return

            try:
                f = getattr(self, f)
            except AttributeError:
                jumped = False
            else:
                jumped = f()
            if not jumped:
                self.pc.inc()
            self.interface.update()

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
        return True

    def JMS(self):
        if self.ac.leftmost == 1:
            self.ar.to(self.pc)
            return True
        return False

    def JPL(self):
        if self.ac.signed_value > 0:
            self.ar.to(self.pc)
            return True
        return False

    def JZE(self):
        if self.ac.signed_value == 0:
            self.ar.to(self.pc)
            return True
        return False

    def JNM(self):
        if self.ac.leftmost == 0:
            self.ar.to(self.pc)
            return True
        return False

    def JNP(self):
        if self.ac.leftmost == 1 or self.ac.value == 0:
            self.ar.to(self.pc)
            return True
        return False

    def JNZ(self):
        if self.ac.signed_value != 0:
            self.ar.to(self.pc)
            return True
        return False

    def JSR(self):
        self.pc.inc()
        self.pc.to(self.dr)
        self.sp.to(self.ar)
        self.savemem()
        self.sp.dec()
        self.pc.set(self.ir.value & self.maddr)
        return True
    
    def RTN(self):
        self.sp.inc()
        self.sp.to(self.ar)
        self.getmem()
        self.dr.to(self.pc)
        return True 
    
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
            return
        self.dr.set(value)
        self.savemem()
    
    def END(self):
        self.running = False
        return True

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
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.dr.to(self.ac)

    def STAS(self):
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.ac.to(self.dr)
        self.savemem()

    def ADDS(self):
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUBS(self):
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
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.dr.to(self.ac)

    def STAB(self):
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.ac.to(self.dr)
        self.savemem()

    def ADDB(self):
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        if self.ac.will_overflow(self.ac.signed_value + self.dr.signed_value):
            raise Overflow
        self.ac += self.dr

    def SUBB(self):
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        if self.ac.will_overflow(self.ac.signed_value - self.dr.signed_value):
            raise Overflow
        self.ac -= self.dr

    def OUTS(self):
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.interface.showOutput(self.dr.signed_value)

    def OUTB(self):
        self.ar.set(self.bp.value + (self.ir.value & self.maddr))
        self.getmem()
        self.interface.showOutput(self.dr.signed_value)

    def INS(self):
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        value = self.interface.getInput()
        self.dr.set(value)
        self.savemem()

    def INB(self):
        self.ar.set(self.sp.value + (self.ir.value & self.maddr))
        value = self.interface.getInput()
        self.dr.set(value)
        self.savemem()


