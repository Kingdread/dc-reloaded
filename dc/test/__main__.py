#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import os
import unittest

from . import get_tests

suite = get_tests()

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
