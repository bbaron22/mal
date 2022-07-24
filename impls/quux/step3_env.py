from mal_types import MalType, MalSymbol, MalList, mal_list, MalEnv
from printer import pr_str
from reader import read_str


def READ(s: str) -> MalType:
    return read_str(s)


def EVAL(ast: MalType, env: MalEnv) -> MalType:
    if not isinstance(ast, MalList):
        return eval_ast(ast, env)
    if len(ast) == 0:
        return ast
    arg0 = ast[0]
    if arg0 == 'def!':
        env.set(ast[1], EVAL(ast[2], env))
        return env.get(ast[1])
    elif arg0 == 'let*':
        localEnv = MalEnv(env)
        bindings = ast[1]
        for i in range(0, len(bindings), 2):
            localEnv.set(bindings[i], eval_ast(bindings[i + 1], localEnv))
        return EVAL(ast[2], localEnv)
    else:
        evaled = eval_ast(ast, env)
        op = evaled[0]
        args = evaled[1:]
        return op(*args)


def PRINT(ast: MalType) -> str:
    return pr_str(ast)


GLOBALS = MalEnv()


def rep(s: str) -> str:
    return PRINT(EVAL(READ(s), GLOBALS))


def eval_ast(ast: MalType, env: MalEnv) -> MalType:
    if isinstance(ast, MalSymbol):
        return env.get(ast)
    if isinstance(ast, MalList):
        elems = [EVAL(elem, env) for elem in ast]
        return mal_list(ast, elems)
    return ast


def main():
    print('')
    # while True:
    #     line = input('user> ')
    #     print(rep(line))

    # lines = [
    #     '(def! a 6)',
    #     'a',
    #     '(def! b (+ a 2))',
    #     '(+ a b)',
    #     '(+ 4 5)',
    #     '(let* (c 2) c)',
    #     '(let* (a 1 b 2) (+ a b))',
    #     '(let* (a 1 b 2) (* (+ a b) (let* (a 1 b 2) (+ a b))))',
    #
    # ]
    # for line in lines:
    #     print(rep(line))


if __name__ == '__main__':
    main()
