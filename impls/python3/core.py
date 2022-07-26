import operator as opers
import mal_types as types
import printer


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
}
