class Result:
    def __init__(self, source=None, target=None, match=None, additional=None):
        self._source = source
        self._target = target
        self._match = match
        self._additional = additional

    def __bool__(self):
        return self.match is not None and self.match

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def match(self):
        return self._match

    @property
    def additional(self):
        return self._additional