def READ(s: str) -> str:
    return s


def EVAL(s: str) -> str:
    return s


def PRINT(s: str) -> str:
    return s


def rep(s: str) -> str:
    return PRINT(EVAL(READ(s)))


def main():
    while True:
        line = input('user> ')
        print(rep(line))


if __name__ == '__main__':
    main()
