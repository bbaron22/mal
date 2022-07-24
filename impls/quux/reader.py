import re

from mal_types import MalType, MalList, MalAtom, MalString, MalSymbol, MalNil, MalVector


class Unbalanced(Exception):
    pass


PATTERN = r'[\s,]*(~@|[\[\]{}()\'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}(\'"`,;)]*)'
RE = re.compile(PATTERN)
STRING_RE = re.compile(r'"(?:[\\].|[^\\"])*"')

BRACKETS = {'(': ')', '[': ']', '{': '}'}


class Reader:
    tokens: list
    pos: int

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def next(self):
        if not self.hasNext():
            raise Unbalanced('unexpected EOF')
        self.pos += 1
        tok = self.tokens[self.pos]
        return tok

    def hasNext(self) -> bool:
        return self.pos < len(self.tokens) - 1

    def read_form(self) -> MalType:
        begin = self.peek()
        if begin in BRACKETS:
            return self.read_seq(begin)
        else:
            return self.read_atom()

    def read_seq(self, begin) -> MalList:
        end = BRACKETS[begin]
        mal_seq = MalList() if begin == '(' else MalVector()
        while self.next() != end:
            mal_seq.append(self.read_form())
        return mal_seq

    def read_atom(self) -> MalAtom:
        tok = self.peek()
        try:
            return int(tok)
        except ValueError:
            if re.match(STRING_RE, tok):
                une = _unescape(tok[1:-1])
                return MalString(une)
            if tok[0] == ':':
                return
            if tok == "nil":
                return MalNil
            if tok == "false":
                return False
            if tok == "true":
                return True
            return MalSymbol(tok)


def validate_str(tok):
    if len(tok) > 0 and tok[0] == '"':
        if len(tok) < 2 or tok[-1] != '"':
            raise Unbalanced()


def read_str(s: str) -> MalType:
    reader = Reader(tokenize(s))
    try:
        return reader.read_form()
    except Unbalanced:
        return MalString('unbalanced')


def tokenize(s: str) -> list:
    return RE.findall(s)[:-1]


def _unescape(s):
    return (s
            .replace('\\\\', '\u029e')
            .replace('\\"', '"')
            .replace('\\n', '\n')
            .replace('\u029e', '\\'))
