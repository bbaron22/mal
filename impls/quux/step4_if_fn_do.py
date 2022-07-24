from mal_types import MalType, MalSymbol, MalList, mal_list, MalEnv, MalSeq, MalVector, mal_vector
from printer import pr_str
from reader import read_str
import core


def READ(s: str) -> MalType:
    return read_str(s)


def EVAL(ast: MalType, env: MalEnv) -> MalType:
    if not isinstance(ast, MalList):
        return eval_ast(ast, env)
    if len(ast) == 0:
        return ast
    if ast[0] == 'def!':
        env.set(ast[1], EVAL(ast[2], env))
        return env.get(ast[1])
    elif ast[0] == 'let*':
        local_env = MalEnv(outer=env)
        bindings = ast[1]
        for i in range(0, len(bindings), 2):
            local_env.set(bindings[i], EVAL(bindings[i + 1], local_env))
        return EVAL(ast[2], local_env)
    elif ast[0] == 'do':
        return eval_ast(ast.rest(), env).last()
    elif ast[0] == 'if':
        predicate, then_branch, else_branch = ast[1], ast[2], ast.get(3)
        is_true = EVAL(predicate, env)
        return EVAL(then_branch if is_true else else_branch, env)
    elif ast[0] == 'fn*':
        binds, body = ast[1], ast[2]
        return lambda *a: EVAL(body, MalEnv(outer=env, binds=binds, exprs=a))
    else:
        evaled = eval_ast(ast, env)
        op = evaled[0]
        args = evaled[1:]
        return op(*args)


def PRINT(ast: MalType) -> str:
    return pr_str(ast)


repl_env = MalEnv()
for k, v in core.ns:
    repl_env.set(MalSymbol(k), v)


def rep(s: str) -> str:
    return PRINT(EVAL(READ(s), repl_env))


# rep("(def! not (fn* (a) (if a false true)))")


def eval_ast(ast: MalType, env: MalEnv) -> MalType:
    if isinstance(ast, MalSymbol):
        return env.get(ast)
    if isinstance(ast, MalList):
        elems = [EVAL(elem, env) for elem in ast]
        return mal_list(ast, elems)
    if isinstance(ast, MalVector):
        elems = [EVAL(elem, env) for elem in ast]
        return mal_vector(ast, elems)
    return ast


def main():
    while True:
        line = input('user> ')
        print(rep(line))


def tst():
    # lines = [
    #     # '(let* (a 1 b 2) (if (> a b) a))',
    #     # '(do 1 2 (let* (a 1 b 2) (if (> a b) a)))'
    #     '(fn* (a) a)'
    #     '((fn* (a) a) 7)'
    # ]
    # line1 = '(fn* (a) a)'
    # line2 = '((fn* (a) a) 8)'
    # print(rep(line1))
    # print(rep(line2))
    # for line in lines:
    #     print(rep(line))
    # rep('(def! fib (fn* (N) (if (= N 0) 1 (if (= N 1) 1 (+ (fib (- N 1)) (fib (- N 2)))))))')
    # print(rep('(fib 4)'))
    # print(rep('(let* (f (fn* () x) x 3) (f))'))
    # print(rep('(not (= 5 (+ 2 2)))'))
    # print(rep('( (fn* (& more) (count more)) 1 2 3)'))
    # print(rep('(= :abc :abc)'))
    print(rep('(pr-str [1 2 "abc" "\\""] "def")'))


if __name__ == '__main__':
    # tst()
    main()
