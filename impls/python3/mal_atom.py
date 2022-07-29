from dataclasses import dataclass

from mal_types import MalType, MalCallable


@dataclass
class MalAtom:
    val: MalType


def mk_atom(val: MalType) -> MalAtom:
    return MalAtom(val)


def is_atom(obj) -> bool:
    return isinstance(obj, MalAtom)


def deref(atom: MalAtom) -> MalType:
    return atom.val


def reset(atom: MalAtom, val: MalType) -> MalType:
    atom.val = val
    return val


def swap(atom: MalAtom, fn: MalCallable, *args):
    atom.val = fn(atom.val, *args)
    return atom.val
