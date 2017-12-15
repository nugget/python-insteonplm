class StateChangeSignal(object):
    def __init__(self):
        self._handlers = []

    def connect(self, handler):
        self._handlers.append(handler)

    def update(self, *args):
        for handler in self._handlers:
            handler(*args)
