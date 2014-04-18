#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from . import util


class RAM(list):
    """
    Class to represent the RAM. It is a sublcass of list and can be
    used in the same way, except that it cannot be extended and has
    a fixed size. Every cell is initialized with a value.
    """
    def __init__(self, maxlen, init=0):
        """
        Initialize a RAM list with the given maxlen. Every cell is set
        to init, which defaults to 0. The init element is not copied,
        so be careful when passing mutable objects like lists.
        """
        super().__init__()
        self.maxlen = maxlen
        self.init = init
        super().extend([init] * maxlen)

    def append(self, item):
        raise NotImplementedError("You can't append to the RAM")

    def clear(self):
        self[:] = [self.init] * self.maxlen

    def extend(self, l):
        raise NotImplementedError("You can't extend the RAM")

    def __iadd__(self, other):
        raise NotImplementedError("You can't append to the RAM")

    def remove(self, i):
        raise NotImplementedError("You can't remove from the RAM")

    def insert(self, index, item):
        raise NotImplementedError("You can't insert into the RAM")


class Register():
    """
    Class to represent a machine register. It has a fixed width and
    thus a maximal value. A register can overflow just like a real
    register.
    """
    def __init__(self, name, bits, value=0):
        """
        Initialize a register with the given name and a bitwidth.
        Optionally a init-value (default = 0) can be given.

        The name is not actually important, but it helps keeping all
        registers apart from each other when displaying stuff or doing
        debugging.
        """
        self.name = name
        self.bits = bits
        self.maxvalue = 2 ** bits - 1
        self.signed_max = 2 ** (bits - 1) - 1
        self.signed_min = -1 * 2 ** (bits - 1)
        self.value = value & self.maxvalue

    def dec(self):
        """
        Decrease the value by one
        """
        self.set(self.value-1)

    def inc(self):
        """
        Increase the value by one
        """
        self.set(self.value+1)

    def set(self, value):
        """
        Set the value
        """
        self.value = value & self.maxvalue

    def neg(self):
        """
        Negate the value. This will build the two's complement of the
        number, not the bitwise negation!
        """
        if self.leftmost:
            self.value = ~self.value
            self.value += 1
        else:
            self.value -= 1
            self.value = ~self.value
        self.value &= self.maxvalue

    def to(self, register):
        """
        Set the other register's value to the own value:
        register.set(self.value)
        """
        register.set(self.value)

    def will_overflow(self, i):
        """
        Returns if the given int will fit in the register or cause it
        to overflow.
        """
        return i > self.signed_max or i < self.signed_min

    @property
    def signed_value(self):
        """
        Return the signed value.
        """
        return util.signed_value(self.value, self.bits)

    @property
    def bin(self):
        """
        Return a string with the binary representation of the own value
        """
        return "{v:0{w}b}".format(w=self.bits, v=self.value)

    @property
    def leftmost(self):
        """
        Value of the leftmost bit
        """
        return self.value >> (self.bits - 1)

    @property
    def rightmost(self):
        """
        Value of the rightmost bit
        """
        return self.value & 1

    def _c(self, value):
        """
        Return a register with the same name and the same bitwidth, but
        with the given value (useful for arithemtic operations)
        """
        return self.__class__(self.name, self.bits, value)

    def __str__(self):
        return "<Register {} {v:0{w}b} ({v})>".format(self.name, v=self.value,
                                                      w=self.bits)

    def __repr__(self):
        return "Register({!r}, {!r}, {!r})".format(self.name, self.bits,
                                                   self.value)

    # All the arithmetic functions are defined for Register OP Register
    # and Register OP int:
    def __add__(self, other):
        try:
            return self._c(self.value + other.value)
        except AttributeError:
            return self._c(self.value + other)

    def __sub__(self, other):
        try:
            return self._c(self.value - other.value)
        except AttributeError:
            return self._c(self.value - other)

    def __div__(self, other):
        try:
            return self._c(self.value / other.value)
        except AttributeError:
            return self._c(self.value / other)

    def __mul__(self, other):
        try:
            return self._c(self.value * other.value)
        except AttributeError:
            return self._c(self.value * other)

    def __and__(self, other):
        try:
            return self._c(self.value & other.value)
        except AttributeError:
            return self._c(self.value & other)

    def __or__(self, other):
        try:
            return self._c(self.value | other.value)
        except AttributeError:
            return self._c(self.value | other)

    def __xor__(self, other):
        try:
            return self._c(self.value ^ other.value)
        except AttributeError:
            return self._c(self.value ^ other)

    def __inv__(self):
        return self._c(~ self.value)

    def __rshift__(self, other):
        try:
            return self._c(self.value >> other.value)
        except AttributeError:
            return self._c(self.value >> other)

    def __lshift__(self, other):
        try:
            return self._c(self.value << other.value)
        except AttributeError:
            return self._c(self.value << other)
