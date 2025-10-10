from typing import Callable
from typing import Any
from math import sqrt, sin, cos, tan, floor, ceil, pi, e
import socket as _socket
import os as _os
import importlib
import sys

AstType = list[dict[str, Any]]

# Python module cache for py_import/py_call
_python_modules = {}

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
            if chunk := _os.read(fd, 4096):
                chunks.append(chunk)
            else:
                break
        return b''.join(chunks).decode('utf-8', errors='replace')
    return _os.read(fd, size).decode('utf-8', errors='replace')

def _file_write(fd: int, data: str):
    """Write to file descriptor"""
    return _os.write(fd, data.encode('utf-8'))

def _file_close(fd: int):
    """Close file descriptor"""
    _os.close(fd)
    return None

def _file_exists(path: str):
    """Check if a file or directory exists"""
    return _os.path.exists(path)

def _file_isfile(path: str):
    """Check if path is a file"""
    return _os.path.isfile(path)

def _file_isdir(path: str):
    """Check if path is a directory"""
    return _os.path.isdir(path)

def _file_listdir(path: str = '.'):
    """List directory contents"""
    return _os.listdir(path)

def _file_mkdir(path: str):
    """Create a directory"""
    _os.mkdir(path)
    return None

def _file_makedirs(path: str):
    """Create a directory and all parent directories"""
    _os.makedirs(path, exist_ok=True)
    return None

def _file_remove(path: str):
    """Remove a file"""
    _os.remove(path)
    return None

def _file_rmdir(path: str):
    """Remove an empty directory"""
    _os.rmdir(path)
    return None

def _file_rename(old_path: str, new_path: str):
    """Rename or move a file or directory"""
    _os.rename(old_path, new_path)
    return None

def _file_getsize(path: str):
    """Get file size in bytes"""
    return _os.path.getsize(path)

def _file_getcwd():
    """Get current working directory"""
    return _os.getcwd()

def _file_chdir(path: str):
    """Change current working directory"""
    _os.chdir(path)
    return None

def _file_abspath(path: str):
    """Get absolute path"""
    return _os.path.abspath(path)

def _file_basename(path: str):
    """Get basename of path"""
    return _os.path.basename(path)

def _file_dirname(path: str):
    """Get directory name of path"""
    return _os.path.dirname(path)

def _file_join(*paths: str):
    """Join path components"""
    return _os.path.join(*paths)

# Socket I/O helper functions
_socket_map = {}  # Map integer IDs to socket objects
_next_socket_id = 1

def _socket_create(family: str = 'inet', type_: str = 'stream'):
    """Create a socket and return its ID"""
    global _next_socket_id

    # Parse family
    if family.lower() == 'inet' or family.lower() not in ['inet6', 'unix']:
        fam = _socket.AF_INET
    elif family.lower() == 'inet6':
        fam = _socket.AF_INET6
    else:
        fam = _socket.AF_UNIX
    # Parse type
    if type_.lower() == 'stream' or type_.lower() not in ['dgram', 'raw']:
        typ = _socket.SOCK_STREAM
    elif type_.lower() == 'dgram':
        typ = _socket.SOCK_DGRAM
    else:
        typ = _socket.SOCK_RAW
    sock = _socket.socket(fam, typ)
    sock_id = _next_socket_id
    _next_socket_id += 1
    _socket_map[sock_id] = sock
    return sock_id

def _socket_connect(sock_id: int, host: str, port):
    """Connect socket to address"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    sock.connect((host, int(port)))
    return None

def _socket_bind(sock_id: int, host: str, port):
    """Bind socket to address"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]
    sock.bind((host, int(port)))
    return None

def _socket_listen(sock_id: int, backlog = 5):
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

def _socket_recv(sock_id: int, size = 4096):
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

def _socket_setsockopt(sock_id: int, level: str, option: str, value):
    """Set socket option"""
    if sock_id not in _socket_map:
        raise RuntimeError(f"Invalid socket ID: {sock_id}")
    sock = _socket_map[sock_id]

    # Parse level
    if level.upper() == 'SOL_SOCKET' or level.upper() not in [
        'IPPROTO_TCP',
        'IPPROTO_IP',
    ]:
        lev = _socket.SOL_SOCKET
    elif level.upper() == 'IPPROTO_TCP':
        lev = _socket.IPPROTO_TCP
    else:
        lev = _socket.IPPROTO_IP
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

# Python library integration functions
def _py_import(module_name: str):
    """Import a Python module and cache it"""
    if module_name not in _python_modules:
        try:
            _python_modules[module_name] = importlib.import_module(module_name)
        except ImportError as e:
            raise RuntimeError(f"Cannot import Python module '{module_name}': {e}") from e
    return None

def _py_call(module_name: str, func_name: str, *args):
    """Call a Python function from an imported module"""
    # Resolve alias if needed (runtime mode only)
    import runtime as runtime_module
    if runtime_module.runtime and hasattr(runtime_module, 'py_imports'):
        if module_name in runtime_module.py_imports:
            import_info = runtime_module.py_imports[module_name]
            if import_info.get('type') == 'name':
                import_name = import_info['name']
                func_name = import_name
            module_name = import_info['module']
    # Import module if not already cached
    if module_name not in _python_modules:
        _py_import(module_name)

    module = _python_modules[module_name]

    # Get the function
    if not hasattr(module, func_name):
        raise RuntimeError(f"Cannot find or call function: {module_name}.{func_name}")

    func = getattr(module, func_name)

    # Call the function with arguments
    try:
        result = func(*args)
        # Convert Python types to fr types
        if isinstance(result, bool):
            return result
        elif isinstance(result, int):
            return result
        elif isinstance(result, float):
            return result
        elif isinstance(result, str):
            return result
        elif isinstance(result, (list, tuple)):
            return list(result)
        elif isinstance(result, dict):
            return result
        elif result is None:
            return None
        else:
            # For other types (including class instances), return as-is
            return result
    except Exception as e:
        raise RuntimeError(f"Error calling {module_name}.{func_name}: {e}") from e

def _py_getattr(obj, attr_name: str):
    """Get an attribute or call a method on a Python object"""
    try:
        attr = getattr(obj, attr_name)

        if callable(attr):
            # Return the method itself - it will be called with py_call_method
            return attr
        # It's an attribute, return its value
        result = attr
        # Convert Python types to fr types
        if isinstance(result, bool):
            return result
        elif isinstance(result, int):
            return result
        elif isinstance(result, float):
            return result
        elif isinstance(result, str):
            return result
        elif isinstance(result, (list, tuple)):
            return list(result)
        elif isinstance(result, dict):
            return result
        elif result is None:
            return None
        else:
            # For other types (including class instances), return as-is
            return result
    except AttributeError as e:
        raise RuntimeError(f"Object has no attribute '{attr_name}'") from e
    except Exception as e:
        raise RuntimeError(f"Error accessing attribute '{attr_name}': {e}") from e

def _py_setattr(obj, attr_name: str, value):
    """Set an attribute on a Python object"""
    try:
        setattr(obj, attr_name, value)
        return None
    except AttributeError as e:
        raise RuntimeError(f"Cannot set attribute '{attr_name}' on object") from e
    except Exception as e:
        raise RuntimeError(f"Error setting attribute '{attr_name}': {e}") from e

def _py_call_method(obj, method_name: str, *args):
    """Call a method on a Python object"""
    try:
        method = getattr(obj, method_name)
        if not callable(method):
            raise RuntimeError(f"'{method_name}' is not a callable method")

        result = method(*args)
        # Convert Python types to fr types
        if isinstance(result, bool):
            return result
        elif isinstance(result, int):
            return result
        elif isinstance(result, float):
            return result
        elif isinstance(result, str):
            return result
        elif isinstance(result, (list, tuple)):
            return list(result)
        elif isinstance(result, dict):
            return result
        elif result is None:
            return None
        else:
            # For other types (including class instances), return as-is
            return result
    except AttributeError as e:
        raise RuntimeError(f"Object has no method '{method_name}'") from e
    except Exception as e:
        raise RuntimeError(f"Error calling method '{method_name}': {e}") from e


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
        "func": lambda value: 'true' if value is True else ('false' if value is False else str(value)),
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
        "can_eval": False  # Cannot evaluate at parse time - arguments may be runtime values
    },
    'append': {
        "type": "builtin",
        "args": {
            "lst": "list",
            "value": "any"
        },
        "func": lambda lst, value: lst.append(value) or lst,
        "return_type": "list",
        "can_eval": True
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
    'exists': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_exists,
        "return_type": "bool",
        "can_eval": False
    },
    'isfile': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_isfile,
        "return_type": "bool",
        "can_eval": False
    },
    'isdir': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_isdir,
        "return_type": "bool",
        "can_eval": False
    },
    'listdir': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_listdir,
        "return_type": "list",
        "can_eval": False
    },
    'mkdir': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_mkdir,
        "return_type": "none",
        "can_eval": False
    },
    'makedirs': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_makedirs,
        "return_type": "none",
        "can_eval": False
    },
    'remove': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_remove,
        "return_type": "none",
        "can_eval": False
    },
    'rmdir': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_rmdir,
        "return_type": "none",
        "can_eval": False
    },
    'rename': {
        "type": "builtin",
        "args": {
            "old_path": "string",
            "new_path": "string"
        },
        "func": _file_rename,
        "return_type": "none",
        "can_eval": False
    },
    'getsize': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_getsize,
        "return_type": "int",
        "can_eval": False
    },
    'getcwd': {
        "type": "builtin",
        "args": {},
        "func": _file_getcwd,
        "return_type": "string",
        "can_eval": False
    },
    'chdir': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_chdir,
        "return_type": "none",
        "can_eval": False
    },
    'abspath': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_abspath,
        "return_type": "string",
        "can_eval": False
    },
    'basename': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_basename,
        "return_type": "string",
        "can_eval": False
    },
    'dirname': {
        "type": "builtin",
        "args": {
            "path": "string"
        },
        "func": _file_dirname,
        "return_type": "string",
        "can_eval": False
    },
    'pathjoin': {
        "type": "builtin",
        "args": {
            "paths": "list"
        },
        "func": lambda paths: _file_join(*paths),
        "return_type": "string",
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
    },
    'py_import': {
        "type": "builtin",
        "args": {
            "module_name": "string"
        },
        "func": _py_import,
        "return_type": "none",
        "can_eval": False
    },
    'py_call': {
        "type": "builtin",
        "args": {},  # Variable arguments
        "func": _py_call,
        "return_type": "any",
        "can_eval": False,
        "variadic": True
    },
    'py_getattr': {
        "type": "builtin",
        "args": {},  # Variable arguments: (object, attribute_name)
        "func": _py_getattr,
        "return_type": "any",
        "can_eval": False,
        "variadic": True
    },
    'py_setattr': {
        "type": "builtin",
        "args": {},  # Variable arguments: (object, attribute_name, value)
        "func": _py_setattr,
        "return_type": "none",
        "can_eval": False,
        "variadic": True
    },
    'py_call_method': {
        "type": "builtin",
        "args": {},  # Variable arguments: (object, method_name, *args)
        "func": _py_call_method,
        "return_type": "any",
        "can_eval": False,
        "variadic": True
    }
}
