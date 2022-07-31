from mal_types import MalType
from mal_parser import load_mal_string


def read_str(s: str) -> MalType:
    return load_mal_string(s)
