from typing import Union, NewType, Callable


class MalList(list):
    def __init__(self, begin: str, end: str):
        super().__init__()
        self.begin = begin
        self.end = end


def mal_list(other: MalList, values: list) -> MalList:
    ml = MalList(other.begin, other.end)
    for value in values:
        ml.append(value)
    return ml


class MalString(str):
    pass


class MalSymbol(str):
    pass


MalInt = int
MalAtom = Union[MalInt, MalSymbol, MalString, Callable[..., 'MalType']]
MalType = Union[MalAtom, MalList]
