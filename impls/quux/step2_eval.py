from mal_types import MalType, MalSymbol, MalList, mal_list
from printer import pr_str
from reader import read_str
from operator import add, sub, mul, truediv

repl_env = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv
}


def READ(s: str) -> MalType:
    return read_str(s)


def EVAL(ast: MalType, env: dict) -> MalType:
    if not isinstance(ast, MalList):
        return eval_ast(ast, env)
    if len(ast) == 0:
        return ast
    evaled = eval_ast(ast, env)
    op = evaled[0]
    args = evaled[1:]
    return op(*args)


def PRINT(ast: MalType) -> str:
    return pr_str(ast)


def rep(s: str) -> str:
    return PRINT(EVAL(READ(s), repl_env))


def eval_ast(ast: MalType, env: dict) -> MalType:
    if isinstance(ast, MalSymbol):
        return env[ast]
    if isinstance(ast, MalList):
        elems = [EVAL(elem, env) for elem in ast]
        return mal_list(ast, elems)
    return ast


def main():
    while True:
        line = input('user> ')
        print(rep(line))
    # line = '(+ 1 (* 3))'
    # print(rep(line))


if __name__ == '__main__':
    main()
