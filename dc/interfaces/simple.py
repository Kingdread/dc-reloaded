from dc.interfaces import Interface
import re

MEM = re.compile(r"(?P<adr>^\d+) (?P<cmd>[A-Za-z]+)( (?P<arg>\d+))?$")

class Simple(Interface):
    """Simple command line interface"""
    def __init__(self, d):
        self.d = d
        d.interface = self

    def getInput(self):
        return int(input("Please enter a value: "))

    def showOutput(self, out):
        print("Output:", out)

    def update(self):
        pass

    def run(self):
        # Mainloop here
        while True:
            try:
                command = input(">>> ")
            except EOFError:
                break

            if command == "":
                # CR, single execution
                self.d.cycle()
            else:
                tree = command.split()
                cmd, args = tree[0], tree[1:]
                cmd = cmd.lower()
                candidates = []
                for candidate in self.commands:
                    if candidate.startswith(cmd):
                        candidates.append(candidate)
                
                if len(candidates) == 1:
                    the_chosen_one = candidates[0]
                    f = self.commands[the_chosen_one]
                    f(self, cmd, args)
                elif len(candidates) > 1:
                    print("Ambigous command: {}".format(cmd))
                else:
                    match = MEM.match(command)
                    if match is None:
                        print("Unknown command: {}".format(command))
                    else:
                        adr = int(match.group("adr"))
                        cmd = match.group("cmd").upper()
                        arg = int(match.group("arg"))
                        arg = 0 if arg is None else arg
                        if cmd == "DEF":
                            self.d.ram[adr] = arg
                        elif cmd in self.d.opcodes:
                            code = self.d.opcodes[cmd]
                            self.d.ram[adr] = (code << self.d.conf.addrwidth) | arg
                        else:
                            print("Unknown instruction: {}".format(cmd))

        print("Exiting...")
    
    def do_load(self, cmd, args):
        if not args:
            print("Please specify a filename")
            return
        f = args[0]
        with open(f, "r") as fo:
            lines = fo.readlines()
        self.d.load(lines)
        print("Loaded {}".format(f))
    
    def do_run(self, cmd, args):
        self.d.run()

    def do_clear(self, cmd, args):
        self.d.reset()
        print("Cleared everything")
    
    def do_goto(self, cmd, args):
        if not args:
            print("Syntax: goto addr")
            return
        try:
            addr = int(args[0])
        except ValueError:
            print("Syntax: goto addr")
            return

        if addr < 0 or addr > self.d.maddr:
            print("Invalid address")
            return
        
        self.d.pc.set(addr)
        self.d.run()

    def do_status(self, cmd, args):
        print("Registers:")
        for r in ["ir", "dr", "pc", "ac", "ar", "sp", "bp"]:
            reg = getattr(self.d, r)
            print("    Register {name}: {val:0{w}b} ({sigval})".format(
              name=reg.name, val=reg.value, w=reg.bits, sigval=reg.signed_value))
        print("RAM: (cells != 0)")
        for adr, cell in enumerate(self.d.ram):
            if cell != 0:
                print("    {adr:3} {cmd:4} {arg:3} | {val:0{w}b}".format(
                    adr=adr, cmd=self.d.getcmd(cell), arg=(cell & self.d.maddr),
                    val=cell, w=self.d.cellwidth))
    commands = {
        "load": do_load,
        "run": do_run,
        "clear": do_clear,
        "goto": do_goto,
        "status": do_status
    }
