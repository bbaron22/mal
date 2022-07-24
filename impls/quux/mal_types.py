from collections.abc import Mapping
from collections import UserList
from typing import Union, Callable, Optional


class MalSeq(UserList):
    def __init__(self, begin, end, *args):
        super().__init__(args)
        self.begin = begin
        self.end = end


class MalList(MalSeq):

    def __init__(self, *args):
        super().__init__('(', ')', *args)

    def rest(self) -> 'MalList':
        return self[1:]

    def get(self, index, default=None):
        return self[index] if 0 <= index < len(self) else default

    def last(self):
        return self[-1]


class MalVector(MalSeq):

    def __init__(self, *args):
        super().__init__('[', ']', *args)


def mal_list(other: MalList, values: list) -> MalList:
    ml = MalList()
    for value in values:
        ml.append(value)
    return ml


def mal_vector(other: MalVector, values: list) -> MalVector:
    ml = MalVector()
    for value in values:
        ml.append(value)
    return ml


class MalString(str):
    pass


class MalSymbol(str):
    pass


def mal_keyword(s: str) -> MalString:
    if s[0] == '\u029e':
        return MalString(s)
    return MalString('\u029e' + s)


MalInt = int
MalBool = bool
MalNil = None
MalAtom = Union[MalInt, MalSymbol, MalString, Callable[..., 'MalType'], MalBool, MalNil]
MalType = Union[MalAtom, MalList]


class MalEnv:
    data: dict[MalSymbol, MalAtom]
    outer: Optional['MalEnv']

    def __init__(self, outer: 'MalEnv' = None, binds=None, exprs=None):
        self.outer = outer
        self.data = dict()
        if binds is not None and exprs is not None:
            for i in range(len(binds)):
                if binds[i] == '&':
                    self.set(binds[i + 1], exprs[i:])
                    break
                else:
                    self.set(binds[i], exprs[i])

    def find(self, key) -> Optional['MalEnv']:
        if key in self.data:
            return self
        if self.outer is None:
            return None
        return self.outer.find(key)

    def get(self, key) -> Optional[MalAtom]:
        env = self.find(key)
        if env is None:
            raise KeyError(key)
        return env.data[key]

    def set(self, key: MalSymbol, value: MalAtom):
        self.data[key] = value


class MalDict(dict):
    outer: Optional['MalDict']

    def __init__(self, outer: Optional['MalDict'] = None) -> None:
        super().__init__()
        self.outer = outer

    def find(self, key) -> Optional['MalDict']:
        if key in self:
            return self
        if self.outer is None:
            return None
        return self.outer.find(key)

    def __missing__(self, key):
        if self.outer is None:
            raise KeyError(key)
        return self.outer.get(key)

    def __contains__(self, o) -> bool:
        if o in self.keys():
            return True
        return self.outer is not None and o in self.outer


class FrozenDict(Mapping):

    def __init__(self, data: dict = None):
        self._data = data or {}

    def __iter__(self):
        return self._data.__iter__()

    def __getitem__(self, __k):
        return self._data.__getitem__(__k)

    def __len__(self) -> int:
        return self._data.__len__()


def main():
    L = MalList(1, 2)
    print(L, L.begin, L.end)
    V = MalVector(3, 4)
    print(V, V.begin, L.end)


if __name__ == '__main__':
    main()
