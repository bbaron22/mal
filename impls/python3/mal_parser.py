"""
The parser below is a predictive, recursive-descent parser. The use of a predictive parser
is possible because JSON has an LL(k) grammar. Specifically, JSON has an LL(1) grammar,
a fact that is hinted at in the `parse_mal` function: `parse_mal` looks ahead by only
one character (not even a whole JSON token) in order to decide how to parse the string.
See: https://en.wikipedia.org/wiki/Recursive_descent_parser

JSON definition: https://www.json.org/
JSON-Python type mapping: https://docs.python.org/2/library/json.html#encoders-and-decoders

JSON is a context-free language (https://shiffman.net/a2z/cfg/), not a regular
language (https://cstheory.stackexchange.com/questions/3987/is-json-a-regular-language).
"""

# Top-level Function
import re


def load_mal_string(s):
    i = skip_leading_whitespace(s, 0)
    assert i < len(s), 'string cannot be emtpy or blank'

    try:
        python_element, i = parse_mal(s, i)
        validate_mal(s, i, condition=(i == len(s)))
        return python_element
    except IndexError:
        raise_invalid_mal_error('Unexpected end of string:', s, len(s))


# Parsing JSON and Translating it to Python
# In the parsing functions below, two invariants are implicitly enforced for values
# at the index `i`:
#   1. When `i` is passed in as an argument to a function, `s[i]` is not whitespace.
#   2. When `i` is returned from a function, `s[i]` is not whitespace.
# Therefore, whenever a function is called or the value returned from a function is
# handled, we can immediately begin using `s[i]` to inspect the next JSON token we need
# to handle.
# Other conditions on the value of `s[i]` are more explicitly enforced below, using
# the `validate_mal` function.

def parse_mal(s, i):
    first_char = s[i]

    if first_char == '{':
        return parse_object(s, i)
    elif first_char == '[':
        return parse_array(s, i)
    elif first_char == '(':
        return parse_array(s, i)
    elif first_char == '"':
        return parse_string(s, i)
    elif first_char == '~' and check_symbol(s, i, '~@'):
        return parse_tilde_at(s, i)
    elif first_char in "'`~^@":
        return parse_special(s, i)
    elif first_char == 'n' and check_symbol(s, i, 'nil'):
        return parse_nil(s, i)
    elif first_char == 't' and check_symbol(s, i, 'true'):
        return parse_true(s, i)
    elif first_char == 'f' and check_symbol(s, i, 'false'):
        return parse_false(s, i)
    elif is_number_char(first_char):
        return parse_number(s, i)
    else:
        return parse_symbol(s, i)


def parse_object(s, i):
    validate_mal(s, i, expected='{')

    i = skip_trailing_whitespace(s, i)
    python_dict = {}

    while s[i] != '}':
        key, i = parse_symbol(s, i)
        validate_mal(s, i, not_expected='}')
        value, i = parse_mal(s, i)

        python_dict[key] = value

        # if s[i] == ',':
        #     i = skip_trailing_whitespace(s, i)
        #     validate_mal(s, i, not_expected='}')
        # else:
        #     validate_mal(s, i, expected='}')

    return python_dict, skip_trailing_whitespace(s, i)


def parse_array(s, i):
    validate_mal(s, i, condition=(s[i] in ['(', '[']))
    end = ')' if s[i] == '(' else ']'

    i = skip_trailing_whitespace(s, i)
    python_list = []

    while s[i] != end:
        python_element, i = parse_mal(s, i)
        python_list.append(python_element)

        # if s[i] == ',':
        #     i = skip_trailing_whitespace(s, i)
        #     validate_mal(s, i, not_expected=end)
        # else:
        #     validate_mal(s, i, expected=end)

    return python_list, skip_trailing_whitespace(s, i)


def parse_string(s, i):
    validate_mal(s, i, expected='"')

    i += 1
    i0 = i

    while s[i] != '"':
        if s[i] == '\\':
            i += 2  # Escaped character takes up two spaces.
        else:
            i += 1

    python_string = bytes(s[i0:i], 'utf-8').decode('unicode-escape')
    return python_string, skip_trailing_whitespace(s, i)


def parse_symbol(s, i):
    i0 = i

    while s[i] not in " \t\n\r\f\v":
        if s[i] == '\\':
            i += 2  # Escaped character takes up two spaces.
        else:
            i += 1

    python_string = bytes(s[i0:i], 'utf-8').decode('unicode-escape')
    return python_string, skip_trailing_whitespace(s, i)


def parse_nil(s, i):
    validate_mal(s, i, condition=(s[i:i + 3] == 'nil'))
    return None, skip_leading_whitespace(s, i + 3)


def parse_tilde_at(s, i):
    validate_mal(s, i, condition=(s[i:i + 2] == '~@'))
    return None, skip_leading_whitespace(s, i + 2)


def parse_special(s, i):
    return s[i], skip_leading_whitespace(s, i + 1)


def parse_true(s, i):
    validate_mal(s, i, condition=(s[i:i + 4] == 'true'))
    return True, skip_leading_whitespace(s, i + 4)


def parse_false(s, i):
    validate_mal(s, i, condition=(s[i:i + 5] == 'false'))
    return False, skip_leading_whitespace(s, i + 5)


def is_number_char(char):
    return '0' <= char <= '9'


def parse_number(s, i):
    validate_mal(s, i, condition=('0' <= s[i] <= '9'))

    j = next((j for j in range(i, len(s)) if not is_number_char(s[j])), len(s))
    use_float = any(s[i] in 'Ee.' for i in range(i, j))
    python_converter = float if use_float else int

    try:
        return python_converter(s[i:j]), skip_leading_whitespace(s, j)
    except ValueError:
        raise_invalid_mal_error('Invalid JSON number:', s, i)


# Skipping over Whitespace between JSON Tokens


_whitespace_matcher = re.compile(r'\s*')


# skip_leading_whitespace = lambda s, i: _whitespace_matcher.match(s, i).end()
# skip_trailing_whitespace = lambda s, i: skip_leading_whitespace(s, i + 1)


def skip_leading_whitespace(s, i):
    return _whitespace_matcher.match(s, i).end()


def skip_trailing_whitespace(s, i):
    return skip_leading_whitespace(s, i + 1)


# Validating Input

def validate_mal(s, i, expected=None, not_expected=None, condition=None):
    check_mal(s, i, expected=expected, not_expected=not_expected, condition=condition) or \
    raise_invalid_mal_error('Unexpected token:', s, i)
    # assert expected is not None or not_expected is not None or condition is not None, \
    #     'expected, not_expected, or condition must be declared'
    #
    # expected is not None and s[i] == expected or not_expected is not None and s[
    #     i] != not_expected or condition is True or raise_invalid_mal_error('Unexpected token:', s, i)


def check_mal(s, i, expected=None, not_expected=None, condition=None):
    if expected is not None:
        return s[i] == expected
    if not_expected is not None:
        return s[i] != not_expected
    if condition is not None:
        return condition is True
    assert False, 'expected, not_expected, or condition must be declared'


def check_symbol(s, i, symbol):
    return i + len(symbol) <= len(s) and s[i:i + len(symbol)] == symbol


def raise_invalid_mal_error(message, s, i):
    err_message = JSON_VALIDATION_ERROR_MESSAGE_TEMPLATE.format(
        message=message,
        json=s,
        caret=caret(i)
    )
    raise JsonValidationError(err_message)


def caret(i):
    return ' ' * i + '^'


class JsonValidationError(Exception):
    pass


JSON_VALIDATION_ERROR_MESSAGE_TEMPLATE = """{message}
{json}
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
        test1
    ]

    for t in strings:
        s = t
        print('Testing on input:', s)
        print(load_mal_string(s))

    print('Tests pass!')


if __name__ == '__main__':
    tests()
