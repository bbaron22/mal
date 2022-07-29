import operator as opers
from functools import reduce

import mal_atom as atom
import mal_types as types
import printer
import reader


def _print(sep: str, readable: bool, *args) -> str:
    return sep.join(printer.pr_str(exp, readable) for exp in args)


def _prn(*args):
    print(_print(" ", True, *args))
    return None


def _pr_str(*args):
    return _print(" ", True, *args)


def _str(*args):
    return _print("", False, *args)


def _println(*args):
    print(_print(" ", False, *args))
    return None


def _slurp(filename: str) -> types.MalStr:
    with open(filename, "r") as f:
        return types.MalStr(f.read())


def _vec(arg) -> types.MalVector:
    return types.mk_vector(*arg)


def _concat(*args) -> types.MalList:
    if len(args) == 0:
        return types.mk_list()
    return types.mk_list(*reduce(lambda x, y: x + y, args))


def _cons(x, xs) -> types.MalList:
    return _concat([x], xs)


ns = {
    "+": types.add,
    "-": types.sub,
    "*": types.mul,
    "/": types.truediv,
    "<": opers.lt,
    ">": opers.gt,
    "<=": opers.le,
    ">=": opers.ge,
    "=": types.is_equal,
    "list": types.mk_list,
    "list?": types.is_list,
    "empty?": types.is_empty,
    "count": types.count,
    "pr-str": _pr_str,
    "str": _str,
    "prn": _prn,
    "println": _println,
    "read-string": reader.read_str,
    "slurp": _slurp,
    "atom": atom.mk_atom,
    "atom?": atom.is_atom,
    "deref": atom.deref,
    "reset!": atom.reset,
    "swap!": atom.swap,
    "vec": _vec,
    "cons": _cons,
    "concat": _concat,

}

if __name__ == '__main__':
    # print(type(_vec((1, 2, 3))))
    # print(types.mk_list(1, 2, 3))
    # print(_concat([1, 2], [3]))
    print(_cons(1, [6, 7]))
