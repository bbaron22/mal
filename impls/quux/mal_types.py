from typing import Union


class MalList(list):
    def __init__(self, begin: str, end: str):
        super().__init__()
        self.begin = begin
        self.end = end


class MalString(str):
    pass


class MalSymbol(str):
    pass


MalInt = int
MalAtom = Union[MalInt, MalSymbol, MalString]
MalType = Union[MalAtom, MalList]
