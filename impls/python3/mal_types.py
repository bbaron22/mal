from typing import Union


class MalStr(str):
    pass


class MalInt(int):
    pass


class MalSym(str):
    pass


class MalKeyword(str):
    pass


class MalList(list):
    pass


class MalVector(list):
    pass


MalBool = bool

MalSeq = Union[MalList, MalVector]


def mal_seq(delim: str) -> MalSeq:
    assert delim in ('(', '['), f"invalid token: {delim}"
    return MalList() if delim == '(' else MalVector()


class MalDict(dict):
    pass


MalNil = None

MalType = Union[MalStr, MalInt, MalSym, MalList, MalVector, MalDict, MalNil, MalBool, MalKeyword]


def is_list(obj) -> bool:
    return isinstance(obj, MalList)


def is_vector(obj) -> bool:
    return isinstance(obj, MalVector)


def is_dict(obj) -> bool:
    return isinstance(obj, MalDict)


def is_keyword(obj) -> bool:
    return isinstance(obj, MalKeyword)


def is_string(obj) -> bool:
    return isinstance(obj, MalStr)


def is_nil(obj) -> bool:
    return obj is None


def is_true(obj) -> bool:
    return obj is True


def is_false(obj) -> bool:
    return obj is False


def mk_list(*args) -> MalList:
    return MalList(args)


def mk_symbol(s: str) -> MalSym:
    return MalSym(s)
