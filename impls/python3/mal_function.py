from dataclasses import dataclass

from mal_env import Env
from mal_types import MalType, MalList, MalCallable


@dataclass
class MalFunction1:
    ast: MalType
    params: MalList
    env: Env
    fn: MalCallable


class MalFunction:
    def __init__(self, EVAL, ast, env, params):
        self.EVAL = EVAL
        self.ast = ast
        self.env = env
        self.params = params

    def __call__(self, *args, **kwargs):
        return self.EVAL(self.ast, Env(self.env, self.params, MalList(args)))

    def gen_env(self, args):
        return Env(outer=self.env, binds=self.params, exprs=args)


def is_callable(obj):
    return callable(obj) or isinstance(obj, MalFunction)
