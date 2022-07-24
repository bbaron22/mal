from mal_types import MalType, MalList, MalString, MalSeq


def _escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def pr_str(obj: MalType, print_readably=False) -> str:
    if obj is None:
        return "nil"
    if isinstance(obj, MalSeq):
        L = ' '.join(pr_str(o, print_readably) for o in obj)
        return f"{obj.begin}{L}{obj.end}"
    if isinstance(obj, MalString):
        if len(obj) > 0 and obj[0] == '\u029e':
            return ':' + obj[1:]
        if print_readably:
            return f'"{_escape(obj)}"'
        return str(obj)
    if isinstance(obj, bool):
        return str(obj).lower()
    if callable(obj):
        return "<#function>"
    return str(obj)
