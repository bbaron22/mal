import sys
import traceback

import mal_readline


def READ(s):
    return s


def EVAL(ast, env):
    return ast


def PRINT(exp):
    return exp


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


if __name__ == '__main__':
    main()
