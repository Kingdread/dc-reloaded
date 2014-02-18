#!/usr/bin/python3

class RAM(list):
    def __init__(self, maxlen, init=0):
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
    def __init__(self, name, bits, value=0):
        self.name = name
        self.bits = bits
        self.maxvalue = 2 ** bits - 1
        self.signed_max = 2 ** (bits - 1) - 1
        self.signed_min = -1 * 2 ** (bits - 1)
        self.value = value & self.maxvalue

    def dec(self):
        self.set(self.value-1)

    def inc(self):
        self.set(self.value+1)

    def set(self, value):
        self.value = value & self.maxvalue
    
    def neg(self):
        if self.leftmost:        
            self.value = ~self.value
            self.value += 1
        else:
            self.value -= 1
            self.value = ~self.value
        self.value &= self.maxvalue

    def to(self, register):
        register.set(self.value)

    def will_overflow(self, i):
        return i > self.signed_max or i < self.signed_min

    @property
    def signed_value(self):
        if self.leftmost:
            value = (~(self.value - 1)) & self.maxvalue
            return -1 * value
        else:
            return self.value
    
    @property
    def bin(self):
        return "{v:0{w}b}".format(w=self.bits, v=self.value)

    @property
    def leftmost(self):
        return self.value >> (self.bits - 1)

    @property
    def rightmost(self):
        return self.value & 1

    def _c(self, value):
        return self.__class__(self.name, self.bits, value)

    def __str__(self):
        return "<Register {} {v:0{w}b} ({v})>".format(self.name, v=self.value, w=self.bits)

    def __repr__(self):
        return "Register({!r}, {!r}, {!r})".format(self.name, self.bits, self.value)

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
