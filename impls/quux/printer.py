from mal_types import MalType, MalList, MalString


def pr_str(obj: MalType) -> str:
    if isinstance(obj, MalList):
        L = ' '.join(pr_str(o) for o in obj)
        return f"{obj.begin}{L}{obj.end}"
    elif isinstance(obj, MalString):
        return f'"{obj}"'
    return str(obj)
