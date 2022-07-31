import sys
import traceback

import mal_readline
import reader
import printer


def READ(s):
    return reader.read_str(s)


def EVAL(ast, env):
    return ast


def PRINT(exp):
    return printer.pr_str(exp)


def rep(s):
    return PRINT(READ(EVAL(s, "")))


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
    print(rep('(+ 1 2)'))


if __name__ == '__main__':
    main()
    # t()
