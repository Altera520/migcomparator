from abc import abstractmethod, ABCMeta
from typing import Tuple, Any


class ValidationResult(metaclass=ABCMeta):
    @abstractmethod
    def __str__(self):
        pass

    def show(self):
        print(self)

    def write(self, opt: str):
        pass


class PairResult(ValidationResult):
    def __init__(self, source: Any, target: Any, match: bool):
        self._source = source
        self._target = target
        self._match = match

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    def __str__(self):
        return f"(source: {self._source}, target: {self._target}, match: {self._match})"

    def __eq__(self, other):
        return self._source == other.source and \
               self._target == other.target

    def __bool__(self):
        return self._match


class SingleResult(ValidationResult):
    def __init__(self, result: Any, match: bool):
        self._result = result
        self._match = match

    @property
    def result(self):
        return self._result

    def __bool__(self):
        return self._match

    def __str__(self):
        pass

    def __eq__(self, other):
        return self._result == other.result
