#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
A collection of various exceptions for the DC
"""


class DCError(Exception):
    """
    Base class for all DC related errors
    """
    def __init__(self, msg="", line_number=None):
        super().__init__()
        self.msg = msg
        self.line_number = line_number

    def __str__(self):
        if self.msg:
            return "{}: {}".format(self.__class__.__name__, self.msg)
        else:
            return self.__class__.__name__


class NoInputValue(DCError):
    """
    Used by the interface to signal that not input value could be
    retrieved.
    """


class ScriptError(DCError):
    """
    A general exception for errors in a program, either during the
    loading of a program or during its execution (runtime errors)
    """


class AssembleError(DCError):
    """
    An exception when something went wrong during the assemblation,
    like an unresolved variable name
    """


class Overflow(DCError):
    """
    An exception raised when an overflow would happen
    """


class InvalidAddress(ScriptError):
    """
    A more specific ScriptError when a parameter to a jump is an
    invalid address.
    """


class Breakpoint(DCError):
    """
    Raised when a breakpoint is reached. To be handled by the interface.
    """
