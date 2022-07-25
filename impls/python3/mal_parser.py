"""
The parser below is a predictive, recursive-descent parser. The use of a predictive parser
is possible because JSON has an LL(k) grammar. Specifically, JSON has an LL(1) grammar,
a fact that is hinted at in the `parse_mal` function: `parse_mal` looks ahead by only
one character (not even a whole JSON token) in order to decide how to parse the string.
See: https://en.wikipedia.org/wiki/Recursive_descent_parser

"""

# Top-level Function
import re

from mal_types import MalType, MalDict, MalSeq, mal_seq, MalStr, MalSym, MalNil, MalBool, MalInt, MalKeyword, MalList, \
    mk_list, mk_symbol

q_word = {
    "'": mk_symbol("quote"),
    "`": mk_symbol("quasiquote"),
    "~": mk_symbol("unquote"),
    "~@": mk_symbol("splice-unquote"),
    "@": mk_symbol("deref"),
    "^": mk_symbol("with-meta"),
}


def load_mal_string(s: str) -> (MalType, int):
    i = skip_leading_whitespace(s, 0)
    assert i < len(s), 'string cannot be emtpy or blank'

    try:
        ast, i = parse_mal(s, i)
        validate_mal(s, i, condition=(i == len(s)))
        return ast
    except IndexError:
        raise_invalid_mal_error('Unexpected end of input:', s, len(s))


# Parsing MAL and Translating it to Python
# In the parsing functions below, two invariants are implicitly enforced for values
# at the index `i`:
#   1. When `i` is passed in as an argument to a function, `s[i]` is not whitespace.
#   2. When `i` is returned from a function, `s[i]` is not whitespace.
# Therefore, whenever a function is called or the value returned from a function is
# handled, we can immediately begin using `s[i]` to inspect the next JSON token we need
# to handle.
# Other conditions on the value of `s[i]` are more explicitly enforced below, using
# the `validate_mal` function.

def parse_mal(s: str, i: int) -> (MalType, int):
    first_char = s[i]

    if first_char == '{':
        return parse_object(s, i)
    elif first_char == '[':
        return parse_array(s, i)
    elif first_char == '(':
        return parse_array(s, i)
    elif first_char == '"':
        return parse_string(s, i)
    elif first_char == ':':
        return parse_keyword(s, i)
    elif first_char in q_word:
        return parse_quote(s, i, first_char)
    elif first_char == 'n' and check_symbol(s, i, 'nil'):
        return parse_nil(s, i)
    elif first_char == 't' and check_symbol(s, i, 'true'):
        return parse_true(s, i)
    elif first_char == 'f' and check_symbol(s, i, 'false'):
        return parse_false(s, i)
    elif is_number_token(s, i):
        return parse_number(s, i)
    else:
        return parse_symbol(s, i)


def parse_object(s: str, i: int) -> (MalDict, int):
    validate_mal(s, i, expected='{')

    i = skip_trailing_whitespace(s, i)
    python_dict = MalDict()

    while s[i] != '}':
        key, i = parse_symbol(s, i)
        validate_mal(s, i, not_expected='}')
        value, i = parse_mal(s, i)

        python_dict[key] = value

    return python_dict, skip_trailing_whitespace(s, i)


def parse_array(s: str, i: int) -> (MalSeq, int):
    validate_mal(s, i, condition=(s[i] in ['(', '[']))
    beg = s[i]
    end = ')' if beg == '(' else ']'

    i = skip_trailing_whitespace(s, i)
    python_list = mal_seq(beg)

    while s[i] != end:
        python_element, i = parse_mal(s, i)
        python_list.append(python_element)

    return python_list, skip_trailing_whitespace(s, i)


def parse_string(s: str, i: int) -> (MalStr, int):
    validate_mal(s, i, expected='"')

    i += 1
    i0 = i

    while s[i] != '"':
        if s[i] == '\\':
            i += 2  # Escaped character takes up two spaces.
        else:
            i += 1

    python_string = bytes(s[i0:i], 'utf-8').decode('unicode-escape')
    return MalStr(python_string), skip_trailing_whitespace(s, i)


def parse_symbol(s: str, i: int) -> (MalSym, int):
    i0 = i

    while i < len(s) and s[i] not in " \t\n\r\f\v":
        if s[i] == '\\':
            i += 2  # Escaped character takes up two spaces.
        else:
            i += 1

    python_string = bytes(s[i0:i], 'utf-8').decode('unicode-escape')
    return MalSym(python_string), skip_trailing_whitespace(s, i)


def parse_keyword(s: str, i: int) -> (MalKeyword, int):
    validate_mal(s, i, condition=(i < len(s) - 1))
    keyword, j = parse_symbol(s, i + 1)
    return MalKeyword(keyword), j


def parse_nil(s: str, i: int) -> (MalNil, int):
    validate_mal(s, i, condition=(s[i:i + 3] == 'nil'))
    return None, skip_leading_whitespace(s, i + 3)


def parse_quote(s: str, i: int, q: str) -> (MalList, int):
    validate_mal(s, i, condition=(q in q_word and i + 1 < len(s)))
    inc = 1
    token = q
    if q == '~' and s[i + 1] == '@':
        token = '~@'
        inc = 2
    form, j = parse_mal(s, i + inc)
    if token == '^':
        meta = form
        form, j = parse_mal(s, j)
        return mk_list(q_word[token], form, meta), j
    return mk_list(q_word[token], form), j


def parse_true(s: str, i: int) -> (MalBool, int):
    return True, skip_leading_whitespace(s, i + 4)


def parse_false(s: str, i: int) -> (MalBool, int):
    return False, skip_leading_whitespace(s, i + 5)


def is_number_char(char: str) -> bool:
    return '0' <= char <= '9'


def is_number_token(s: str, i: int) -> bool:
    if is_number_char(s[i]):
        return True
    if s[i] == '-':
        return i < len(s) - 1 and is_number_char(s[i + 1])
    return False


def parse_number(s: str, i: int) -> (MalInt, int):
    validate_mal(s, i, condition=(is_number_token(s, i)))
    i0 = i
    if s[i] == '-':
        i0 += 1
    j = next((j for j in range(i0, len(s)) if not is_number_char(s[j])), len(s))

    try:
        return MalInt(int(s[i:j])), skip_leading_whitespace(s, j)
    except ValueError:
        raise_invalid_mal_error('Invalid number:', s, i)


_whitespace_matcher = re.compile(r'[\s,]*')


def skip_leading_whitespace(s: str, i: int) -> int:
    return _whitespace_matcher.match(s, i).end()


def skip_trailing_whitespace(s: str, i: int) -> int:
    return skip_leading_whitespace(s, i + 1)


# Validating Input

def validate_mal(s: str, i: int, expected=None, not_expected=None, condition=None):
    if not check_mal(s, i, expected=expected, not_expected=not_expected, condition=condition):
        raise_invalid_mal_error('Unexpected token or end of input:', s, i)


def check_mal(s, i, expected=None, not_expected=None, condition=None) -> bool:
    if expected is not None:
        return s[i] == expected
    if not_expected is not None:
        return s[i] != not_expected
    if condition is not None:
        return condition is True
    assert False, 'expected, not_expected, or condition must be declared'


def check_symbol(s, i, symbol) -> bool:
    return i + len(symbol) <= len(s) and s[i:i + len(symbol)] == symbol


def raise_invalid_mal_error(message: str, s: str, i: int):
    err_message = VALIDATION_ERROR_MESSAGE_TEMPLATE.format(
        message=message,
        mal=s,
        caret=caret(i)
    )
    raise MalValidationError(err_message)


def caret(i):
    return ' ' * i + '^'


class MalValidationError(Exception):
    pass


VALIDATION_ERROR_MESSAGE_TEMPLATE = """{message}
{mal}
{caret}"""


# Testing and Performance Measurement

def tests():
    test1 = """{
        hi "there'"
        foo {
            bar "baz"
            blah [
                {foo "bar"}
            ]
        }
    }"""
    strings = [
        # "( + 1 2 )",
        # 'nil',
        # '( + 2 (* 3 4) )',
        # test1
        '-2',
        '2',
        '1234',
        '-1234',
    ]

    for t in strings:
        s = t
        print('Testing on input:', s)
        print(load_mal_string(s))

    print('Tests pass!')


if __name__ == '__main__':
    tests()
