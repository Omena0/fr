from typing import Callable
from typing import Any
from math import sqrt, sin, cos, tan, floor, ceil, pi, e
import socket as _socket
import os as _os

AstType = list[dict[str, Any]]

# File I/O helper functions
def _file_open(path: str, mode: str = 'r'):
    """Open a file and return file handle (as integer fd)"""
    flags = _os.O_RDONLY
    if mode == 'w':
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC
    elif mode == 'a':
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_APPEND
    elif mode == 'r+':
        flags = _os.O_RDWR
    elif mode == 'w+':
        flags = _os.O_RDWR | _os.O_CREAT | _os.O_TRUNC
    return _os.open(path, flags, 0o666)

def _file_read(fd: int, size: int = -1):
    """Read from file descriptor"""
    if size < 0:
        # Read all
        chunks = []
        while True:
            chunk = _os.read(fd, 4096)
            if not chunk:
                break
            chunks.append(chunk)
        return b''.join(chunks).decode('utf-8', errors='replace')
    return _os.read(fd, size).decode('utf-8', errors='replace')

def _file_write(fd: int, data: str):
    """Write to file descriptor"""
    return _os.write(fd, data.encode('utf-8'))

def _file_close(fd: int):
    """Close file descriptor"""
    _os.close(fd)
    return None

# Socket I/O helper functions
_socket_map = {}  # Map integer IDs to socket objects
_next_socket_id = 1

def _socket_create(family: str = 'inet', type_: str = 'stream'):
    """Create a socket and return its ID"""
    global _next_socket_id
    
    # Parse family
    if family.lower() == 'inet':
        fam = _socket.AF_INET
    elif family.lower() == 'inet6':
        fam = _socket.AF_INET6
    elif family.lower() == 'unix':
        fam = _socket.AF_UNIX
    else:
        fam = _socket.AF_INET
    
    # Parse type
    if type_.lower() == 'stream':
        typ = _socket.SOCK_STREAM
    elif type_.lower() == 'dgram':
        typ = _socket.SOCK_DGRAM
    elif type_.lower() == 'raw':
        typ = _socket.SOCK_RAW
    else:
        typ = _socket.SOCK_STREAM
    
    sock = _socket.socket(fam, typ)
    sock_id = _next_socket_id
    _next_socket_id += 1
    _socket_map[sock_id] = sock
    return sock_id

def _socket_connect(sock_id: int, host: str, port: int):
    """Connect socket to address"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    sock.connect((host, int(port)))
    return None

def _socket_bind(sock_id: int, host: str, port: int):
    """Bind socket to address"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    sock.bind((host, int(port)))
    return None

def _socket_listen(sock_id: int, backlog: int = 5):
    """Listen for connections"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    sock.listen(int(backlog))
    return None

def _socket_accept(sock_id: int):
    """Accept a connection and return new socket ID"""
    global _next_socket_id
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    conn, _ = sock.accept()
    conn_id = _next_socket_id
    _next_socket_id += 1
    _socket_map[conn_id] = conn
    return conn_id

def _socket_send(sock_id: int, data: str):
    """Send data through socket"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    return sock.send(data.encode('utf-8'))

def _socket_recv(sock_id: int, size: int = 4096):
    """Receive data from socket"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    data = sock.recv(int(size))
    return data.decode('utf-8', errors='replace')

def _socket_close(sock_id: int):
    """Close socket"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    sock.close()
    del _socket_map[sock_id]
    return None

def _socket_setsockopt(sock_id: int, level: str, option: str, value: int):
    """Set socket option"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    
    # Parse level
    if level.upper() == 'SOL_SOCKET':
        lev = _socket.SOL_SOCKET
    elif level.upper() == 'IPPROTO_TCP':
        lev = _socket.IPPROTO_TCP
    elif level.upper() == 'IPPROTO_IP':
        lev = _socket.IPPROTO_IP
    else:
        lev = _socket.SOL_SOCKET
    
    # Parse option
    opt_map = {
        'SO_REUSEADDR': _socket.SO_REUSEADDR,
        'SO_KEEPALIVE': _socket.SO_KEEPALIVE,
        'SO_BROADCAST': _socket.SO_BROADCAST,
        'SO_RCVBUF': _socket.SO_RCVBUF,
        'SO_SNDBUF': _socket.SO_SNDBUF,
    }
    opt = opt_map.get(option.upper(), _socket.SO_REUSEADDR)
    
    sock.setsockopt(lev, opt, int(value))
    return None

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
    },
    
    # File I/O functions
    'fopen': {
        "type": "builtin",
        "args": {
            "path": "string",
            "mode": "string"
        },
        "func": _file_open,
        "return_type": "int",
        "can_eval": False
    },
    'fread': {
        "type": "builtin",
        "args": {
            "fd": "int",
            "size": "int"
        },
        "func": _file_read,
        "return_type": "string",
        "can_eval": False
    },
    'fwrite': {
        "type": "builtin",
        "args": {
            "fd": "int",
            "data": "string"
        },
        "func": _file_write,
        "return_type": "int",
        "can_eval": False
    },
    'fclose': {
        "type": "builtin",
        "args": {
            "fd": "int"
        },
        "func": _file_close,
        "return_type": "none",
        "can_eval": False
    },
    
    # Socket I/O functions
    'socket': {
        "type": "builtin",
        "args": {
            "family": "string",
            "type": "string"
        },
        "func": _socket_create,
        "return_type": "int",
        "can_eval": False
    },
    'connect': {
        "type": "builtin",
        "args": {
            "sock_id": "int",
            "host": "string",
            "port": "int"
        },
        "func": _socket_connect,
        "return_type": "none",
        "can_eval": False
    },
    'bind': {
        "type": "builtin",
        "args": {
            "sock_id": "int",
            "host": "string",
            "port": "int"
        },
        "func": _socket_bind,
        "return_type": "none",
        "can_eval": False
    },
    'listen': {
        "type": "builtin",
        "args": {
            "sock_id": "int",
            "backlog": "int"
        },
        "func": _socket_listen,
        "return_type": "none",
        "can_eval": False
    },
    'accept': {
        "type": "builtin",
        "args": {
            "sock_id": "int"
        },
        "func": _socket_accept,
        "return_type": "int",
        "can_eval": False
    },
    'send': {
        "type": "builtin",
        "args": {
            "sock_id": "int",
            "data": "string"
        },
        "func": _socket_send,
        "return_type": "int",
        "can_eval": False
    },
    'recv': {
        "type": "builtin",
        "args": {
            "sock_id": "int",
            "size": "int"
        },
        "func": _socket_recv,
        "return_type": "string",
        "can_eval": False
    },
    'sclose': {
        "type": "builtin",
        "args": {
            "sock_id": "int"
        },
        "func": _socket_close,
        "return_type": "none",
        "can_eval": False
    },
    'setsockopt': {
        "type": "builtin",
        "args": {
            "sock_id": "int",
            "level": "string",
            "option": "string",
            "value": "int"
        },
        "func": _socket_setsockopt,
        "return_type": "none",
        "can_eval": False
    }
}
