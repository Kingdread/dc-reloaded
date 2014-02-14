class DCError(Exception):
    def __init__(self,  msg=""):
        self.msg = msg

    def __str__(self):
        if self.msg:
            return "{}: {}".format(self.__class__.__name__, self.msg)
        else:
            return self.__class__.__name__


class NoInputValue(DCError): pass


class ScriptError(DCError): pass


class AssembleError(DCError): pass


class Overflow(DCError): pass
