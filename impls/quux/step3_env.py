from mal_types import MalType, MalSymbol, MalList, mal_list
from printer import pr_str
from reader import read_str
from operator import add, sub, mul, truediv
from collections import ChainMap

repl_env = ChainMap({
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv
})


def READ(s: str) -> MalType:
    return read_str(s)


def EVAL(ast: MalType, env: ChainMap) -> MalType:
    if not isinstance(ast, MalList):
        return eval_ast(ast, env)
    if len(ast) == 0:
        return ast
    arg0 = ast[0]
    if arg0 == 'def!':
        env[ast[1]] = EVAL(ast[2], env)
        return env[ast[1]]
    elif arg0 == 'let*':
        localEnv = env.new_child()
        bindings = ast[1]
        for i in range(0, len(bindings), 2):
            localEnv[bindings[i]] = eval_ast(bindings[i + 1], localEnv)
        return EVAL(ast[2], localEnv)
    else:
        evaled = eval_ast(ast, env)
        op = evaled[0]
        args = evaled[1:]
        return op(*args)


def PRINT(ast: MalType) -> str:
    return pr_str(ast)


def rep(s: str) -> str:
    return PRINT(EVAL(READ(s), repl_env))


def eval_ast(ast: MalType, env: ChainMap) -> MalType:
    if isinstance(ast, MalSymbol):
        return env[ast]
    if isinstance(ast, MalList):
        elems = [EVAL(elem, env) for elem in ast]
        return mal_list(ast, elems)
    return ast


def main():
    # while True:
    #     line = input('user> ')
    #     print(rep(line))

    lines = [
        '(def! a 6)',
        'a',
        '(def! b (+ a 2))',
        '(+ a b)',
        '(+ 4 5)',
        '(let* (c 2) c)',
        '(let* (a 1 b 2) (+ a b))',
        '(let* (a 1 b 2) (* (+ a b) (let* (a 1 b 2) (+ a b))))',

    ]
    for line in lines:
        print(rep(line))


if __name__ == '__main__':
    main()
