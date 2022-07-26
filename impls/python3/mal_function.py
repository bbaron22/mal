from dataclasses import dataclass

from mal_env import Env
from mal_types import MalType, MalList, MalCallable


@dataclass
class MalFunction:
    ast: MalType
    params: MalList
    env: Env
    fn: MalCallable


def is_callable(obj):
    return callable(obj) or isinstance(obj, MalFunction)
