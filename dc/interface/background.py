import threading
import time
from dc.errors import DCError

class DCThread(threading.Thread):
    def __init__(self, interface):
        super().__init__()
        self.daemon = True
        self.d = interface.d
        self.interface = interface
        self._r = threading.Event()

    def resume(self):
        self.d.running = True
        self._r.set()

    def pause(self):
        self._r.clear()

    def run(self):
        while self._r.wait():
            try:
                self.d.cycle()
            except DCError as de:
                self.interface.report(de)
                self.d.running = False
            if not self.d.running:
                self._r.clear()
            time.sleep(self.interface.delay)
