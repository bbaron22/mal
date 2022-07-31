from typing import Union, Callable

KEYWORD_MARKER = '\u029e'

MalStr = str
MalKeyword = str


class MalSym(str):
    pass


class MalVector(list):

    def __getitem__(self, i):
        if type(i) == slice:
            return MalVector(super().__getitem__(i))
        return super().__getitem__(i)

    def __add__(self, x):
        return MalVector(super().__add__(x))


MalList = list

MalInt = int

MalBool = bool

MalDict = dict

MalNil = None

MalCallable = Callable[..., 'MalType']
MalSeq = Union[MalList, MalVector]
MalType = Union[
    MalStr, MalInt, MalSym, MalList, MalVector, MalDict, MalNil, MalBool, MalKeyword, MalCallable, 'MalAtom']


def is_seq(obj):
    return isinstance(obj, list)


def is_vector(obj):
    return isinstance(obj, MalVector)


def is_list(obj):
    return is_seq(obj) and not is_vector(obj)


def is_empty(obj):
    return is_seq(obj) and len(obj) == 0


def is_dict(obj):
    return isinstance(obj, dict)


def is_symbol(obj):
    return isinstance(obj, MalSym)


def is_keyword(obj):
    return isinstance(obj, str) and obj.startswith(KEYWORD_MARKER)


def is_string(obj):
    return isinstance(obj, str) and not (is_keyword(obj) or is_symbol(obj))


def mk_vector(*args):
    return MalVector(args)


def mk_int(obj):
    return int(obj)


def mk_nil():
    return None


def mk_list(*args):
    return list(args)


def mk_string(s):
    if is_keyword(s):
        return s.replace(KEYWORD_MARKER, ":")
    return str(s)


def mk_symbol(s):
    return MalSym(s)


def mk_keyword(s):
    if s.startswith(':'):
        return s.replace(':', KEYWORD_MARKER)
    else:
        return KEYWORD_MARKER + s


def is_nil(obj):
    return obj is None


def is_true(obj):
    return obj is True


def is_false(obj):
    return obj is False


def is_truthy(obj) -> bool:
    if obj is True or obj is False:
        return obj
    return obj is not None


def is_falsey(obj) -> bool:
    return obj is None or obj is False


def mk_dict():
    return dict()


def count(obj):
    return 0 if is_nil(obj) else len(obj)


def mal_seq(delim: str) -> MalSeq:
    assert delim in ('(', '['), f"invalid token: {delim}"
    return mk_list() if delim == '(' else mk_vector()
