from typing import Optional

from mal_types import MalSym, MalType, MalList

from typing import Sequence


class Env:
    data: dict[MalSym, MalType]
    outer: Optional['Env']

    def __init__(self, outer: 'Env' = None,
                 binds: Optional[Sequence[MalSym]] = None,
                 exprs: Optional[Sequence[MalType]] = None):
        self.outer = outer
        self.data = dict()
        binds = binds or []
        exprs = exprs or []
        if binds:
            for i in range(len(binds)):
                if binds[i] == '&':
                    self.set(binds[i + 1], MalList(exprs[i:]))
                    break
                else:
                    self.set(binds[i], exprs[i])

    def set(self, key: str, value: MalType):
        key = key if isinstance(key, MalSym) else MalSym(key)
        self.data[key] = value

    def find(self, key: MalSym) -> Optional['Env']:
        if key in self.data:
            return self
        return self.outer.find(key) if self.outer is not None else None

    def get(self, key: MalSym) -> MalSym:
        env = self.find(key)
        if env is None:
            raise KeyError(f"'{key}' not found")
        return env.data[key]
