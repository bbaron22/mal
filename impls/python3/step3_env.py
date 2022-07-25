import sys
import traceback
from operator import add, sub, mul, truediv

import mal_readline
import mal_types as types
import printer
import reader
from mal_env import Env
from mal_types import MalType


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
    if ast[0] == 'def!':
        if len(ast) != 3:
            raise Exception("def! requires two args")
        env.set(ast[1], EVAL(ast[2], env))
        return env.get(ast[1])
    if ast[0] == 'let*':
        if len(ast) != 3:
            raise Exception("let* requires two args")
        let_env = Env(env)
        bindings = ast[1]
        if len(bindings) % 2 != 0:
            raise Exception("odd number of binding args")
        for i in range(0, len(bindings), 2):
            let_env.set(types.mk_symbol(bindings[i]), EVAL(bindings[i + 1], let_env))
        return EVAL(ast[2], let_env)
    args = eval_ast(ast, env)
    fn = args[0]
    return fn(*args[1:])


def PRINT(exp):
    return printer.pr_str(exp)


def init_env() -> Env:
    ops = {
        "+": add,
        "-": sub,
        "*": mul,
        "/": truediv,
    }
    env = Env()
    for k, v in ops.items():
        env.set(types.mk_symbol(k), v)
    return env


repl_env = init_env()


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
        except Exception as e:
            print(e)
            # print("".join(traceback.format_exception(*sys.exc_info())))


def t():
    lines = [
        '(def! a 6)',
        'a',
        '(def! b (+ a 2))',
        '(+ a b)',
        '(let* (c 2) c)'
    ]
    for line in lines:
        print(rep(line))


if __name__ == '__main__':
    main()
    # t()
