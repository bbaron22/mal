import core
import mal_readline
import mal_types as types
import printer
import reader
from mal_env import Env
from mal_function import MalFunction
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
    while True:
        if not types.is_list(ast):
            return eval_ast(ast, env)
        if types.is_empty(ast):
            return ast
        if ast[0] == 'def!':
            if len(ast) != 3:
                raise Exception("def! requires two args")
            env.set(ast[1], EVAL(ast[2], env))
            return env.get(ast[1])
        elif ast[0] == 'let*':
            if len(ast) != 3:
                raise Exception("let* requires two args")
            env = Env(outer=env)
            bindings = ast[1]
            if len(bindings) % 2 != 0:
                raise Exception("odd number of binding args")
            for i in range(0, len(bindings), 2):
                env.set(types.mk_symbol(bindings[i]), EVAL(bindings[i + 1], env))
            ast = ast[2]
        elif ast[0] == 'do':
            eval_ast(ast.slice(a=1, b=-1), env)
            ast = ast[-1]
        elif ast[0] == 'if':
            in_fact = EVAL(ast[1], env)
            fact = ast[2]
            fiction = ast[3] if len(ast) > 3 else None
            ast = fact if types.is_truthy(in_fact) else fiction
        elif ast[0] == 'fn*':
            a1, a2 = ast[1], ast[2]
            fn = lambda *a: EVAL(ast[2], Env(outer=env, binds=ast[1], exprs=a))
            return MalFunction(ast=a2, params=a1, env=env, fn=fn)
        else:
            args = eval_ast(ast, env)
            f = args[0]
            if isinstance(f, MalFunction):
                env = Env(outer=f.env, binds=f.params, exprs=args[1:])
                ast = f.ast
            elif callable(f):
                return f(*args[1:])
            else:
                raise Exception(ast + ": invalid object")


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
    # rep("(def! not (fn* (a) (if a false true)))", repl_env)
    # rep("(def! echo (fn* (a) a))", repl_env)
    lines = [
        ('(let* (z 9) z)', "9"),
        ('(if false 7 8)', "8"),
        ('(if false 7 false)', "false"),
        ('( ( (fn* (a) (fn* (b) (+ a b))) 5) 7)', "12"),
        ('((fn* (a) a) 1)', "1"),
        ('(do 1)', "1"),
        ('(do (prn 101) (prn 102) (+ 1 2))', "3"),
        ('(def! a -12)', "-12"),
        ('(def! sum_down (fn* (N) (if (> N 0) (+ N (sum_down  (- N 1))) 0)))', "<#function>"),
        ('(sum_down 1)', "1"),
        ('(sum_down 2)', "3"),
        ('(sum_down 6)', "21"),
        ('(def! fib (fn* (N) (if (= N 0) 1 (if (= N 1) 1 (+ (fib (- N 1)) (fib (- N 2)))))))', "<#function>"),
        ('(fib 1)', "1"),
        ('(fib 2)', "2"),
        ('(fib 4)', "5"),
        ('(let* (f (fn* () x) x 3) (f))', "3"),
        ('(let* (cst (fn* (n) (if (= n 0) nil (cst (- n 1))))) (cst 1))', "nil"),
        ('(let* (f (fn* (n) (if (= n 0) 0 (g (- n 1)))) g (fn* (n) (f n))) (f 2))', "0"),
        ('(def! func (fn* (a) a))', "<#function>"),
    ]
    for line_no, (line, expected) in enumerate(lines):
        # print(rep(line, repl_env))
        got = rep(line, repl_env)
        assert expected == got, f'line: {line_no} expected {expected} got {got}'


if __name__ == '__main__':
    main()
    # t()
