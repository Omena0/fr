from typing import Any
import struct
import zstd

AstType = list[dict[str, Any]]

# Magic number "L2AS" (fr AST) in ASCII
MAGIC_NUMBER = b'L2AS'
# Format version
FORMAT_VERSION = 1

# Type tags for binary encoding
TYPE_NONE = 0
TYPE_BOOL_FALSE = 1
TYPE_BOOL_TRUE = 2
TYPE_INT = 3
TYPE_FLOAT = 4
TYPE_STR = 5
TYPE_LIST = 6
TYPE_DICT = 7

def _compute_checksum(data: bytes) -> int:
    """Compute a simple CRC32 checksum"""
    import zlib
    return zlib.crc32(data) & 0xFFFFFFFF

def _encode_value(value: Any) -> bytes:
    """Encode a single value to bytes"""
    if value is None:
        return bytes([TYPE_NONE])
    elif isinstance(value, bool):
        return bytes([TYPE_BOOL_TRUE if value else TYPE_BOOL_FALSE])
    elif isinstance(value, float):
        # Encode float as double (8 bytes)
        data = bytes([TYPE_FLOAT])
        data += struct.pack('<d', value)
        return data
    elif isinstance(value, int):
        # Variable-length integer encoding
        data = bytes([TYPE_INT])
        # Convert to string for large integers
        int_str = str(value).encode('utf-8')
        data += struct.pack('<I', len(int_str))
        data += int_str
        return data
    elif isinstance(value, str):
        encoded = value.encode('utf-8')
        data = bytes([TYPE_STR])
        data += struct.pack('<I', len(encoded))
        data += encoded
        return data
    elif isinstance(value, (list, tuple)):
        # Convert tuples to lists (like JSON would)
        data = bytes([TYPE_LIST])
        data += struct.pack('<I', len(value))
        for item in value:
            data += _encode_value(item)
        return data
    elif isinstance(value, dict):
        data = bytes([TYPE_DICT])
        data += struct.pack('<I', len(value))
        for key, val in value.items():
            # Keys are always strings in AST
            key_encoded = key.encode('utf-8')
            data += struct.pack('<I', len(key_encoded))
            data += key_encoded
            data += _encode_value(val)
        return data
    else:
        raise ValueError(f"Unsupported type: {type(value)}")

def _decode_value(data: bytes, offset: int) -> tuple[Any, int]:
    """Decode a value from bytes, returns (value, new_offset)"""
    type_tag = data[offset]
    offset += 1
    
    if type_tag == TYPE_NONE:
        return None, offset
    elif type_tag == TYPE_BOOL_FALSE:
        return False, offset
    elif type_tag == TYPE_BOOL_TRUE:
        return True, offset
    elif type_tag == TYPE_FLOAT:
        value = struct.unpack('<d', data[offset:offset+8])[0]
        offset += 8
        return value, offset
    elif type_tag == TYPE_INT:
        str_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        int_str = data[offset:offset+str_len].decode('utf-8')
        offset += str_len
        return int(int_str), offset
    elif type_tag == TYPE_STR:
        str_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        string = data[offset:offset+str_len].decode('utf-8')
        offset += str_len
        return string, offset
    elif type_tag == TYPE_LIST:
        list_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        result = []
        for _ in range(list_len):
            item, offset = _decode_value(data, offset)
            result.append(item)
        return result, offset
    elif type_tag == TYPE_DICT:
        dict_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        result = {}
        for _ in range(dict_len):
            key_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            key = data[offset:offset+key_len].decode('utf-8')
            offset += key_len
            value, offset = _decode_value(data, offset)
            result[key] = value
        return result, offset
    else:
        raise ValueError(f"Unknown type tag: {type_tag}")

def encode_binary(ast: AstType) -> bytes:
    """Encode AST to compressed binary format with header"""
    # Encode the top-level list
    raw_data = _encode_value(ast)
    # Compress with zstd
    compressed = zstd.compress(raw_data, 22)  # Level 22 for maximum compression
    
    # Compute checksum of compressed data
    checksum = _compute_checksum(compressed)
    
    # Build final format:
    # - Magic number (4 bytes): "L2AS"
    # - Version (1 byte): format version
    # - Checksum (4 bytes): CRC32 of compressed data
    # - Compressed data
    header = MAGIC_NUMBER + struct.pack('<B', FORMAT_VERSION) + struct.pack('<I', checksum)
    return header + compressed

def decode_binary(data: bytes) -> AstType:
    """Decode compressed binary format to AST with validation"""
    # Verify minimum size (4 magic + 1 version + 4 checksum = 9 bytes minimum)
    if len(data) < 9:
        raise ValueError("Invalid binary format: file too small")
    
    # Check magic number
    magic = data[:4]
    if magic != MAGIC_NUMBER:
        raise ValueError(f"Invalid magic number: expected {MAGIC_NUMBER}, got {magic}")
    
    # Check version
    version = data[4]
    if version != FORMAT_VERSION:
        raise ValueError(f"Unsupported format version: {version} (expected {FORMAT_VERSION})")
    
    # Verify checksum
    stored_checksum = struct.unpack('<I', data[5:9])[0]
    compressed = data[9:]
    computed_checksum = _compute_checksum(compressed)
    
    if stored_checksum != computed_checksum:
        raise ValueError(f"Checksum mismatch: file may be corrupted (expected {stored_checksum:08x}, got {computed_checksum:08x})")
    
    # Decompress
    raw_data = zstd.decompress(compressed)
    # Decode the top-level list
    result, _ = _decode_value(raw_data, 0)
    return result


