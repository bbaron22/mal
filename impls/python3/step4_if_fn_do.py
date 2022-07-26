import core
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
        return env.get(ast)
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
        let_env = Env(outer=env)
        bindings = ast[1]
        if len(bindings) % 2 != 0:
            raise Exception("odd number of binding args")
        for i in range(0, len(bindings), 2):
            let_env.set(types.mk_symbol(bindings[i]), EVAL(bindings[i + 1], let_env))
        return EVAL(ast[2], let_env)
    if ast[0] == 'do':
        el = eval_ast(ast.rest(), env)
        return el[-1]
    if ast[0] == 'if':
        in_fact = EVAL(ast[1], env)
        fact = ast[2]
        fiction = ast[3] if len(ast) > 3 else None
        branch = fact if types.is_truthy(in_fact) else fiction
        return EVAL(branch, env)
    if ast[0] == 'fn*':
        return lambda *a: EVAL(ast[2], Env(outer=env, binds=ast[1], exprs=a))
    args = eval_ast(ast, env)
    fn = args[0]
    return fn(*args[1:])


def PRINT(exp):
    return printer.pr_str(exp)


def init_env() -> Env:
    env = Env()
    for k, v in core.ns.items():
        env.set(types.mk_symbol(k), v)
    return env


def rep(s, env):
    return PRINT(EVAL(READ(s), env))


def main():
    repl_env = init_env()
    rep("(def! not (fn* (a) (if a false true)))", repl_env)
    while True:
        # noinspection PyBroadException
        try:
            line = mal_readline.readline("user> ")
            if line is None:
                break
            if line == "":
                continue
            print(rep(line, repl_env))
        except Exception as e:
            print(e)
            # print("".join(traceback.format_exception(*sys.exc_info())))


def t():
    repl_env = init_env()
    rep("(def! not (fn* (a) (if a false true)))", repl_env)
    rep("(def! echo (fn* (a) a))", repl_env)
    lines = [
        '( (fn* (& more) (count more)) 1 2 3)',
        '( (fn* (& more) (list? more)) 1 2 3)',
    ]
    for line in lines:
        print(rep(line, repl_env))


if __name__ == '__main__':
    main()
    # t()
