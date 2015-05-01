#!/usr/bin/python
# -*- encoding: utf-8 -*-
import unittest

from .. import DC, DCConfig


class MockInterface(object):
    def __init__(self, input):
        self.input = input
        self.output = []

    def add_input(self, item):
        self.input.append(item)

    def get_input(self):
        return self.input.pop(0)

    def show_output(self, item):
        self.output.append(item)


class DcTestCase(unittest.TestCase):
    def setUp(self):
        self.dc_config = DCConfig()
        self.dc = DC(self.dc_config)
        self.interface = MockInterface([])
        self.dc.interface = self.interface

    def test_command_name(self):
        """Assert that a cell value can be correctly translated to a command"""
        import random

        for command_name, opcode in self.dc.opcodes.items():
            address = random.randint(0, self.dc.max_address)
            cell = opcode << self.dc.conf.address_width | address
            with self.subTest(command_name=command_name, address=address):
                self.assertEqual(self.dc.command_name(cell), command_name)
        # Special case: DEF
        self.assertEqual(self.dc.command_name(1 << self.dc.cellwidth), "DEF")

    def test_parse_command(self):
        """Assert that a correct command is parsed correctly"""
        self.assertEqual(self.dc.parse_command("JMP 15"), 0b0001000001111)

    def test_strip_comment(self):
        """Assert that comments are correctly stripped"""
        # List of test -> expected result pairs
        tests = [
            ("Hey Ya", "Hey Ya"),
            ("Hey ;Ya", "Hey "),
            (";Hey Ya", ""),
        ]
        for test, expect in tests:
            with self.subTest(test=test):
                self.assertEqual(self.dc.strip_comment(test), expect)

    def test_tokenize(self):
        lines = [
            "The Devil:",
            "Is",
            "Near:",
        ]
        expected = [("The", 1), ("Devil", 1), ("Is", 2), ("Near", 3)]
        tokens = list(self.dc.tokenize(lines))
        self.assertEqual(tokens, expected)

    def test_assemble(self):
        """Assert that the assembler is outputting the right program"""
        # This is actually harder than you might think. As I see it, there are
        # two possible ways to achieve it:
        # 1) Hardcore the expected output for a given input program
        # 2) Assemble and run the program and check its output
        # Option 1 leaves no room for "optimisations" and option 2 relies on
        # the "runtime" being correct. I've chosen option 1 because I don't
        # expect any optimisations from the assembler.
        def normalize_list(l):
            result = []
            for item in l:
                item = item.strip()
                # Strip off leading zeroes
                while item.startswith("0"):
                    item = item[1:]
                if item:
                    result.append(item)
            return result

        program = (
            "NUM: DEF 0\n"
            "LOOP:     \n"
            "INM NUM   \n"
            "LDA NUM   \n"
            "INC       \n"
            "STA NUM   \n"
            "OUT NUM   \n"
            "JMP LOOP  \n"
        ).split("\n")
        output = (
            "0 DEF 0\n"
            "1 INM 0\n"
            "2 LDA 0\n"
            "3 INC  \n"
            "4 STA 0\n"
            "5 OUT 0\n"
            "6 JMP 1\n"
        ).split("\n")

        self.assertEqual(
            normalize_list(self.dc.assemble(program)),
            normalize_list(output),
        )

    def test_load(self):
        """Assert that loading a file works correctly"""
        program = ["0 JMP 15", "1 OUT 3"]
        self.dc.load(program)
        self.assertEqual(self.dc.ram[0], 0b0001000001111)
        self.assertEqual(self.dc.ram[1], 0b0010100000011)

    def test_run(self):
        """All-in-one test to check if a small program runs correctly"""
        program = [
            "0 INM 10",
            "1 LDA 10",
            "2 INC",
            "3 STA 10",
            "4 OUT 10",
            "5 INM 10",
            "6 OUT 10",
            "7 END",
        ]
        self.interface.add_input(2)
        self.interface.add_input(3)
        self.interface.add_input(5)
        self.dc.load(program)
        self.dc.run()
        self.assertEqual(self.interface.input, [5])
        self.assertEqual(self.interface.output, [3, 3])
