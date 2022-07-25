from typing import Optional

from mal_types import MalSym, MalType


class Env:
    data = dict[MalSym, MalType]
    outer = Optional['Env']

    def __init__(self, outer: 'Env' = None):
        self.outer = outer
        self.data = dict()

    def set(self, key: MalSym, value: MalType):
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
