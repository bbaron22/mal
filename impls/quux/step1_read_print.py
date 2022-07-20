from mal_types import MalType
from reader import read_str
from printer import pr_str


def READ(s: str) -> MalType:
    return read_str(s)


def EVAL(obj: MalType) -> MalType:
    return obj


def PRINT(obj: MalType) -> str:
    return pr_str(obj)


def rep(s: str) -> str:
    return PRINT(EVAL(READ(s)))


def main():
    while True:
        line = input('user> ')
        print(rep(line))
    # lines = ['123', '123 ', 'abc', 'abc ', '(123 456)', '( 123 456 789 )', '( + 2 (* 3 4) )']
    # for line in lines:
    #     print(rep(line))


if __name__ == '__main__':
    main()
