#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import unittest

from ..parts import Register

class RegisterTestCase(unittest.TestCase):
    def setUp(self):
        self.register = Register("Test", 8)

    def test_value_limits(self):
        """Assert that the calculated numerical limits are correct"""
        self.assertEqual(self.register.maxvalue, 255)
        self.assertEqual(self.register.signed_max, 127)
        self.assertEqual(self.register.signed_min, -128)
    
    def test_decrease_increase(self):
        """Assert that decreasing and increasing works"""
        self.register.dec()
        self.assertEqual(self.register.signed_value,  -1)
        self.register.inc()
        self.assertEqual(self.register.signed_value, 0)

    def test_truncate_at_set_value(self):
        """Assert that a value is properly truncated when out of bounds"""
        # bit pattern 111111111 (511)
        #           &  11111111 (255)
        #             ---------
        #              11111111 (255, -1)
        self.register.set(511)
        self.assertEqual(self.register.signed_value, -1)
        self.assertEqual(self.register.value, 255)

    def test_binary_repr(self):
        """Assert that the binary representation is fine"""
        self.register.set(-3)
        self.assertEqual(self.register.bin, "11111101")

    def test_outer_bit_accessor(self):
        """Assert that leftmost and rightmost are working"""
        self.register.set(1)
        self.assertEqual(self.register.leftmost, 0)
        self.assertEqual(self.register.rightmost, 1)
