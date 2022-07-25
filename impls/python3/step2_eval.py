import sys
import traceback
from operator import add, sub, mul, truediv

import mal_readline
import reader
import printer
import mal_types as types
from mal_types import MalList, MalVector, MalType


def READ(s):
    return reader.read_str(s)


def eval_ast(ast: MalType, env) -> MalType:
    if types.is_symbol(ast):
        val = env.get(ast)
        if val is None:
            raise Exception(f"symbol '{ast}' not found")
        return val
    if types.is_list(ast):
        return types.mk_list(*[EVAL(x, env) for x in ast])
    if types.is_vector(ast):
        return types.mk_vector(*[EVAL(x, env) for x in ast])
    if types.is_dict(ast):
        d = {}
        for k, v in ast.items():
            d[k] = EVAL(v, env)
        print(d)
        return types.mk_dict(*[(k, EVAL(v, env)) for k, v in ast.items()])
    return ast


def EVAL(ast: MalType, env) -> MalType:
    if not types.is_list(ast):
        return eval_ast(ast, env)
    if types.is_empty(ast):
        return ast
    el = eval_ast(ast, env)
    fn = el[0]
    return fn(*el[1:])


def PRINT(exp):
    return printer.pr_str(exp)


repl_env = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": truediv,
}


def rep(s):
    return PRINT(EVAL(READ(s), repl_env))


def main():
    while True:
        # noinspection PyBroadException
        try:
            line = mal_readline.readline("user> ")
            if line is None:
                break
            if line == "":
                continue
            print(rep(line))
        except Exception:
            print("".join(traceback.format_exception(*sys.exc_info())))


def t():
    print(rep('{"a" (+ 7 8)}'))


if __name__ == '__main__':
    main()
    # t()
