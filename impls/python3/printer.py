import mal_types as types


def escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def pr_str(obj, print_readably=True):
    pr = print_readably
    if types.is_list(obj) or types.is_vector(obj):
        beg, end = ('(', ')') if types.is_list(obj) else ('[', ']')
        return beg + " ".join(pr_str(o, pr) for o in obj) + end
    if types.is_dict(obj):
        ret = []
        for k, v in obj.items():
            ret.extend((pr_str(k), pr_str(v, pr)))
        return "{" + " ".join(ret) + "}"
    if types.is_keyword(obj):
        return f":{obj}"
    if types.is_string(obj):
        if print_readably:
            return f'"{escape(obj)}"'
        else:
            return obj
    if types.is_true(obj):
        return "true"
    if types.is_false(obj):
        return "false"
    if types.is_nil(obj):
        return "nil"
    return str(obj)
