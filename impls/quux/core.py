from operator import add, sub, mul, truediv, lt, le, ge, gt, eq

from mal_types import MalList, MalNil
from printer import pr_str


def _prn(*args) -> MalNil:
    res = ' '.join(pr_str(e, True) for e in args)
    print(res)
    return None


def _pr_str(*args) -> str:
    return ' '.join(pr_str(e, True) for e in args)


def _str(*args) -> str:
    return ''.join(pr_str(e, False) for e in args)


def _println(*args) -> MalNil:
    res = ' '.join(pr_str(e, False) for e in args)
    print(res)
    return None


def _list(*args) -> MalList:
    return MalList(*args)


def _list_Q(arg):
    return isinstance(arg, list)


def _empty_Q(arg):
    return arg is None or len(arg) == 0


def _count(arg):
    return 0 if arg is None else len(arg)


ns = [
    ('=', eq),
    ('+', add),
    ('-', sub),
    ('*', mul),
    ('/', truediv),
    ('<', lt),
    ('<=', le),
    ('>', gt),
    ('>=', ge),
    ('prn', _prn),
    ('pr-str', _pr_str),
    ('str', _str),
    ('println', _println),
    ('list', _list),
    ('list?', _list_Q),
    ('empty?', _empty_Q),
    ('count', _count)
]
