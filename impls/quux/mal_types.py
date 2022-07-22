from collections.abc import Mapping
from typing import Union, Callable, Optional
from operator import add, sub, mul, truediv


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


class MalEnv:
    repl_env = {
        '+': add,
        '-': sub,
        '*': mul,
        '/': truediv
    }

    data: dict[str, MalAtom]
    outer: Optional['MalEnv']

    def __init__(self, outer: 'MalEnv' = None):
        self.outer = outer
        self.data = dict() if outer else dict(self.repl_env)

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

    def set(self, key: str, value: MalAtom):
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
    outer = MalDict()
    inner = MalDict(outer)
    outer['a'] = 1
    inner['b'] = 2
    assert 'a' in inner
    fd = FrozenDict({'a': 1, 'b': 2})
    assert fd['a'] == 1
    assert len(fd) == 2
    for item in fd.items():
        print(item)


if __name__ == '__main__':
    main()
