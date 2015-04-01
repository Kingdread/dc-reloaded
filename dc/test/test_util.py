#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest

from .. import util

class UtilTestCase(unittest.TestCase):
    def test_signed_value_positive(self):
        self.assertEqual(
            util.signed_value(0b0101, 4),
            5,
        )

    def test_signed_value_negative(self):
        self.assertEqual(
            util.signed_value(0b1011, 4),
            -5,
        )

    def test_number_of_digits_base_ten(self):
        from math import e
        cases = [0, 1, 9, 10, 99, 100, 101, 567, int(e ** 42)]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    util.number_of_digits(case, 10),
                    len(str(case)),
                )

    def test_number_of_digits_base_two(self):
        from math import pi
        cases = [0, 1, 2, 3, 5, 127, 128, int(pi ** 42)]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    util.number_of_digits(case, 2),
                    len(bin(case)) - 2,  # Strip off 0b prefix
                )

    def test_number_of_digits_arbitrary_base(self):
        cases = [
            # Num Base Solution
            (19, 3, 3),
            (42, 7, 2),
            (2015, 16, 3),
            (1997, 5, 5),
        ]
        for number, base, solution in cases:
            with self.subTest(number=number, base=base):
                self.assertEqual(
                    util.number_of_digits(number, base),
                    solution,
                )
