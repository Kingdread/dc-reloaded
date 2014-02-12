class DCError(Exception):
    def __init__(self,  msg):
        self.msg = msg

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.msg)


class NoInputValue(DCError): pass


class ScriptError(DCError): pass


class AssembleError(DCError): pass
