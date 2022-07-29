import sys

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


def qq_loop(ast) -> types.MalList:
    concat = types.mk_symbol("concat")
    cons = types.mk_symbol("cons")
    ans = types.mk_list()
    for elt in reversed(ast):
        if types.is_list(elt) and len(elt) > 1 and elt[0] == 'splice-unquote':
            ans = types.mk_list(concat, elt[1], ans)
        else:
            ans = types.mk_list(cons, quasiquote(elt), ans)
    return ans


def quasiquote(ast: MalType) -> MalType:
    quote = types.mk_symbol("quote")
    vec = types.mk_symbol("vec")
    if types.is_list(ast):
        if len(ast) == 2 and ast[0] == 'unquote':
            return ast[1]
        else:
            return qq_loop(ast)
    elif types.is_dict(ast) or types.is_symbol(ast):
        return types.mk_list(quote, ast)
    elif types.is_vector(ast):
        return types.mk_list(vec, qq_loop(ast))
    else:
        return ast


def EVAL(ast: MalType, env) -> MalType:
    while True:
        if not types.is_list(ast):
            return eval_ast(ast, env)
        if types.is_empty(ast):
            return ast
        if ast[0] == 'def!':
            assert len(ast) == 3, "def! requires two args"
            env.set(ast[1], EVAL(ast[2], env))
            return env.get(ast[1])
        elif ast[0] == 'let*':
            if len(ast) != 3:
                raise Exception("let* requires two args")
            env = Env(outer=env)
            bindings = ast[1]
            assert len(bindings) % 2 == 0, "odd number of binding args"
            for i in range(0, len(bindings), 2):
                env.set(types.mk_symbol(bindings[i]), EVAL(bindings[i + 1], env))
            ast = ast[2]
        elif ast[0] == 'quote':
            return ast[1]
        elif ast[0] == 'quasiquote':
            ast = quasiquote(ast[1])
        elif ast[0] == 'quasiquoteexpand':
            return quasiquote(ast[1])
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
            return MalFunction(EVAL=EVAL, ast=a2, env=env, params=a1)
        else:
            el = eval_ast(ast, env)
            f = el[0]
            if isinstance(f, MalFunction):
                ast = f.ast
                env = f.gen_env(el[1:])
            elif callable(f):
                return f(*el[1:])
            else:
                raise Exception(ast + ": invalid object")


def PRINT(exp):
    return printer.pr_str(exp)


def init_env() -> Env:
    env = Env()
    for k, v in core.ns.items():
        env.set(k, v)
    env.set('eval', lambda ast: EVAL(ast, env))
    rep("(def! not (fn* (a) (if a false true)))", env)
    rep('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))', env)
    return env


def rep(s, env):
    return PRINT(EVAL(READ(s), env))


def main():
    repl_env = init_env()

    repl_env.set("*ARGV*", types.mk_list())
    if len(sys.argv) > 1:
        repl_env.set("*ARGV*", types.mk_list(*sys.argv[2:]))
        rep(f'(load-file "{sys.argv[1]}"', repl_env)
        sys.exit(0)
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
        print(f"{line_no}: {line}, {expected}")
        got = rep(line, repl_env)
        assert expected == got, f'line: {line_no} expected {expected} got {got}'


def t1():
    repl_env = init_env()
    lines = [
        # '(read-string "7 ;; comment")',
        # '(def! mal-prog (list + 1 2))',
        # '(eval mal-prog)',
        # '(inc4 3)',
        # '(def! inc3 (fn* (a) (+ 3 a)))',
        # '(inc3 2)',
        # '(def! a (atom 2))',
        # '(atom? a)',
        # '(atom? 1)',
        # '(deref a)',
        # '(reset! a 3)',
        # '(deref a)',
        # '(str (quote abc))',
        '(= (quote abc) "abc")',
    ]
    for line in lines:
        print(rep(line, repl_env))


if __name__ == '__main__':
    main()
    # t1()
    # t()
