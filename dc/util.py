#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# pylint: disable=too-few-public-methods
"""
Various utility functions and classes for DC
"""


def signed_value(val, bits):
    """
    Convert a "raw" value (which might be a two's complement) and a
    bitwidth and return the signed value, e.g.

    >>> signed_value(0b0101, 4)
    5
    >>> signed_value(0b1011, 4)
    -5
    """
    leftmost = val >> (bits - 1)
    if leftmost:
        # To get the two's complement of a number, we need to invert it
        # and add 1. The reverse is first subtracting 1 and then
        # inverting it to get the absolute of the number
        val = (~(val - 1)) & (2 ** bits - 1)
        # Because val is now the absolute of the number, we have to
        # make it negative again
        val = -1 * val
    return val


class IDict(dict):
    """
    Case-Insensitive dict. Keys can be everything that has a .lower()
    method.
    """
    def __init__(self, init=None, **kwargs):
        super().__init__()
        if init is not None:
            try:
                init = init.items()
            except AttributeError:
                pass
            for key, val in init:
                self[key] = val
        for key, val in kwargs.items():
            self[key] = val

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __delitem__(self, key):
        super().__delitem__(key.lower())

    def get(self, key, d):
        return super().get(key.lower(), d)

    def __contains__(self, key):
        return super().__contains__(key.lower())
