from typing import Callable
from typing import Any
from math import sqrt, sin, cos, tan, floor, ceil, pi, e

AstType = list[dict[str, Any]]

funcs:dict[ # Holy type annotations
    str,
    dict[
        str,
        str | dict[str,str] | Callable | bool | AstType | list[str] | list[tuple[str, str | None]]
    ]
] = {
    'println': {
        "type": "builtin",
        "args": {
            "text": "string"
        },
        "func": print,
        "return_type": "none",
        "can_eval": False
    },
    'sqrt': {
        "type": "builtin",
        "args": {
            "num": "float"
        },
        "func": sqrt,
        "return_type": "float",
        "can_eval": True
    },
    'input': {
        "type": "builtin",
        "args": {
            "text": "str"
        },
        "func": input,
        "return_type": "str",
        "can_eval": False
    },
    'round': {
        "type": "builtin",
        "args": {
            "num": "float"
        },
        "func": round,
        "return_type": "int",
        "can_eval": True
    },
    'str': {
        "type": "builtin",
        "args": {
            "value": "any"
        },
        "func": str,
        "return_type": "string",
        "can_eval": True
    },
    'len': {
        "type": "builtin",
        "args": {
            "value": "any"
        },
        "func": len,
        "return_type": "int",
        "can_eval": True
    },
    'append': {
        "type": "builtin",
        "args": {
            "lst": "list",
            "value": "any"
        },
        "func": lambda lst, value: lst.append(value) or lst,
        "return_type": "list",
        "can_eval": False
    },
    'pop': {
        "type": "builtin",
        "args": {
            "lst": "list"
        },
        "func": lambda lst: lst.pop() if lst else None,
        "return_type": "any",
        "can_eval": False
    },
    'int': {
        "type": "builtin",
        "args": {
            "value": "any"
        },
        "func": lambda value: int(float(value)) if isinstance(value, str) and '.' in value else int(value),
        "return_type": "int",
        "can_eval": True
    },
    'float': {
        "type": "builtin",
        "args": {
            "value": "any"
        },
        "func": float,
        "return_type": "float",
        "can_eval": True
    },
    'bool': {
        "type": "builtin",
        "args": {
            "value": "any"
        },
        "func": lambda value: str(bool(value)).lower(),
        "return_type": "bool",
        "can_eval": True
    },
    'upper': {
        "type": "builtin",
        "args": {
            "text": "string"
        },
        "func": lambda text: str(text).upper(),
        "return_type": "string",
        "can_eval": True
    },
    'lower': {
        "type": "builtin",
        "args": {
            "text": "string"
        },
        "func": lambda text: str(text).lower(),
        "return_type": "string",
        "can_eval": True
    },
    'strip': {
        "type": "builtin",
        "args": {
            "text": "string"
        },
        "func": lambda text: str(text).strip(),
        "return_type": "string",
        "can_eval": True
    },
    'split': {
        "type": "builtin",
        "args": {
            "text": "string",
            "separator": "string"
        },
        "func": lambda text, sep=' ': str(text).split(str(sep)),
        "return_type": "list",
        "can_eval": False  # Don't evaluate at parse time
    },
    'join': {
        "type": "builtin",
        "args": {
            "separator": "string",
            "items": "list"
        },
        "func": lambda sep, items: str(sep).join([str(x) for x in items]),
        "return_type": "string",
        "can_eval": True
    },
    'replace': {
        "type": "builtin",
        "args": {
            "text": "string",
            "old": "string",
            "new": "string"
        },
        "func": lambda text, old, new: str(text).replace(str(old), str(new)),
        "return_type": "string",
        "can_eval": True
    },
    'abs': {
        "type": "builtin",
        "args": {
            "value": "any"
        },
        "func": abs,
        "return_type": "any",
        "can_eval": True
    },
    'pow': {
        "type": "builtin",
        "args": {
            "base": "any",
            "exponent": "any"
        },
        "func": pow,
        "return_type": "any",
        "can_eval": True
    },
    'min': {
        "type": "builtin",
        "args": {
            "a": "any",
            "b": "any"
        },
        "func": min,
        "return_type": "any",
        "can_eval": True
    },
    'max': {
        "type": "builtin",
        "args": {
            "a": "any",
            "b": "any"
        },
        "func": max,
        "return_type": "any",
        "can_eval": True
    },
    'floor': {
        "type": "builtin",
        "args": {
            "value": "float"
        },
        "func": floor,
        "return_type": "int",
        "can_eval": True
    },
    'ceil': {
        "type": "builtin",
        "args": {
            "value": "float"
        },
        "func": ceil,
        "return_type": "int",
        "can_eval": True
    },
    'sin': {
        "type": "builtin",
        "args": {
            "value": "float"
        },
        "func": sin,
        "return_type": "float",
        "can_eval": True
    },
    'cos': {
        "type": "builtin",
        "args": {
            "value": "float"
        },
        "func": cos,
        "return_type": "float",
        "can_eval": True
    },
    'tan': {
        "type": "builtin",
        "args": {
            "value": "float"
        },
        "func": tan,
        "return_type": "float",
        "can_eval": True
    },
    'PI': {
        "type": "builtin",
        "args": {},
        "func": lambda: pi,
        "return_type": "float",
        "can_eval": True
    },
    'E': {
        "type": "builtin",
        "args": {},
        "func": lambda: e,
        "return_type": "float",
        "can_eval": True
    }
}
