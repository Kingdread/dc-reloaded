class Interface():
    """Base class for different GUI/CLI for the DC"""
    def __init__(self, d):
        raise NotImplementedError("This is the base class. Use a derived class"
        " instead.")

    def getInput(self):
        raise NotImplementedError

    def showOutput(self, out):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
