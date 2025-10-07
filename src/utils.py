import random
import string

class InputStream:
    def __init__(self, text:str, parent_stream=None, offset_in_parent:int=0):
        # original full text (for diagnostics / exceptions)
        self.original:str = text

        # remaining text to parse
        self.text:str = text

        # consumed text (convenience)
        self.past:str = ''

        # absolute index (number of characters consumed from original)
        self.index:int = 0

        # Track parent stream for proper error reporting
        self.parent_stream = parent_stream
        self.offset_in_parent = offset_in_parent

        # File path for error messages
        self.file_path:str|None = None

        # 1-based line and char (column) position of the next character in original
        if parent_stream:
            # Inherit line number from parent stream
            # Calculate line number by counting newlines in parent up to offset_in_parent
            parent_text_before = parent_stream.original[:parent_stream.index - len(text) + offset_in_parent]
            self.line:int = parent_text_before.count('\n') + 1
            # Calculate character position
            last_nl = parent_text_before.rfind('\n')
            if last_nl == -1:
                self.char:int = len(parent_text_before) + 1
            else:
                self.char:int = len(parent_text_before) - last_nl
        else:
            self.line:int = 1
            self.char:int = 1

    def add_line_info(self, node: dict) -> dict:
        """Add line number information to an AST node"""
        if isinstance(node, dict) and 'line' not in node:
            node['line'] = self.line
        return node

    def _recompute_position(self):
        # ensure index is within bounds
        if self.index < 0:
            self.index = 0
        if self.index > len(self.original):
            self.index = len(self.original)

        # rebuild past and text from original to keep them consistent
        self.past = self.original[:self.index]
        self.text = self.original[self.index:]

        # recompute line and char (1-based)
        last_nl = self.original.rfind('\n', 0, self.index)
        if last_nl == -1:
            self.line = 1
            self.char = self.index + 1
        else:
            # number of newlines consumed is count of '\n' in past
            self.line = self.past.count('\n') + 1
            # char is index offset from last newline (position after newline is column 1)
            self.char = self.index - last_nl

    def _advance(self, n: int):
        """
        Advance the stream by n characters, updating text, past, index, line and char.
        """
        if n == 0:
            return
        # clamp forward movement
        n_forward = max(min(n, len(self.text)), -len(self.past))
        self.index += n_forward
        self._recompute_position()

    def peek(self, length:int) -> str:
        return self.text[:length]

    def peek_char(self, length:int) -> str:
        return ''.join(self.text.split())[:length]

    def peek_word(self):
        return split_multi(self.text, ' \n()[]{}', )[0]

    def consume(self, text:str):
        success = self.text.startswith(text)
        if success:
            self._advance(len(text))
        return success

    def consume_word(self):
        word = split_multi(self.text, ' \n()[]{}', maxsplit=1)[0]
        # compute how much whitespace is removed after the word
        after = self.text.removeprefix(word)
        stripped_after = after.lstrip()
        whitespace_removed = len(after) - len(stripped_after)
        total_advance = len(word) + whitespace_removed
        self._advance(total_advance)
        return word

    def consume_until(self, char:str):
        if len(char) > 1:
            raise ValueError('Char must be of length 1')
        out = ''
        for c in self.text:
            if c == char:
                break
            out += c
        # advance by the characters consumed (not including the delimiter)
        self._advance(len(out))
        return out

    def seek(self, num:int):
        text = self.text[:num]
        self._advance(len(text))
        return text

    def seek_word(self):
        text = split_multi(self.text, ' \n()[]{}', maxsplit=1)[0]
        self._advance(len(text))
        return text

    def startswith(self, text:str):
        return self.text.startswith(text)

    def strip(self, chars:str=' \n'):
        # only left-strip affects position/index right-strip only changes remaining text
        left_stripped = self.text.lstrip(chars)
        left_trim = len(self.text) - len(left_stripped)
        if left_trim:
            self._advance(left_trim)
        # now right-strip the remaining text (does not affect index)
        self.text = self.text.rstrip(chars)

    def seek_back(self, num:int):
        """
        Seek backwards by up to num characters. Returns the string that was rewound
        (the characters moved back into self.text).
        """
        if num <= 0:
            return ''
        to_move = min(num, len(self.past))
        if to_move == 0:
            return ''
        old_index = self.index
        self.index -= to_move
        self._recompute_position()
        return self.original[self.index:old_index]

    def seek_back_line(self):
        """
        Seek back to the start of the previous line. Returns the string that was rewound.
        If already on the first line, seeks to the start (index 0).
        """
        # start of current line
        start_current = self.original.rfind('\n', 0, self.index)
        start_current = (start_current + 1) if start_current != -1 else 0

        # find previous newline before start_current
        prev_nl = self.original.rfind('\n', 0, start_current - 1) if start_current > 0 else -1
        new_index = (prev_nl + 1) if prev_nl != -1 else 0

        if new_index == self.index:
            return ''
        old_index = self.index
        self.index = new_index
        self._recompute_position()
        return self.original[self.index:old_index]

    def orig_line(self, line:int|None = None) -> str:
        """Get a specific line from the original text (1-based line number)"""
        line_num = line if line is not None else self.line
        lines = self.original.split('\n')
        if 0 < line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def get_root_stream(self):
        """Get the root stream (the original file stream)"""
        if self.parent_stream is None:
            return self
        return self.parent_stream.get_root_stream()

    def get_absolute_position(self):
        """Get the absolute line and char in the root stream"""
        if self.parent_stream is None:
            return self.line, self.char

        # Get position in parent
        parent_abs_line, parent_abs_char = self.parent_stream.get_absolute_position()

        # If we're on line 1 in this substring, we're on the same line as where substring starts
        if self.line == 1:
            return parent_abs_line, parent_abs_char + self.char - 1
        else:
            # We've advanced to a new line in the substring
            return parent_abs_line + self.line - 1, self.char

    def format_error(self, message:str) -> str:
        """Format an error message with proper file location"""
        abs_line, abs_char = self.get_absolute_position()
        root = self.get_root_stream()

        # Get the actual line from the root stream
        lines = root.original.split('\n')
        if 0 < abs_line <= len(lines):
            error_line = lines[abs_line - 1]
            pointer = ' ' * (abs_char - 1) + '^'

            location = f"{root.file_path}:{abs_line}:{abs_char}" if root.file_path else f"Line {abs_line}:{abs_char}"
            return f"{location}: {message}\n  {error_line}\n  {pointer}"
        else:
            location = f"{root.file_path}:{abs_line}:{abs_char}" if root.file_path else f"Line {abs_line}:{abs_char}"
            return f"{location}: {message}"

def strip_all(all:list[str]):
    return [i.strip() for i in all]

def split_multi(text:str, seps:str, maxsplit:int=-1):
    sep = '.'
    while sep in text:
        sep += random.choice(string.ascii_letters+'0123456789')

    for s in seps:
        text = text.replace(s, sep)

    return text.split(sep, maxsplit)

def split(text: str, sep: str, maxsplit: int = -1) -> list[str]:
    if not sep:
        raise ValueError("empty separator")
    result:list[str] = []
    current = ""
    i = 0
    in_string = False
    quote_char = None
    paren_depth = 0
    splits = 0
    while i < len(text):
        if in_string:
            # Handle escape sequences
            if text[i] == '\\' and i + 1 < len(text):
                current += text[i]  # Add backslash
                i += 1
                current += text[i]  # Add escaped character
                i += 1
            elif text[i] == quote_char:
                in_string = False
                quote_char = None
                current += text[i]
                i += 1
            else:
                current += text[i]
                i += 1
        else:
            if text[i] in "\"'":
                in_string = True
                quote_char = text[i]
                current += text[i]
                i += 1
            elif text[i] == '(':
                paren_depth += 1
                current += text[i]
                i += 1
            elif text[i] == ')':
                paren_depth -= 1
                current += text[i]
                i += 1
            elif text.startswith(sep, i) and paren_depth == 0:
                result.append(current)
                current = ""
                i += len(sep)
                splits += 1
                if maxsplit != -1 and splits >= maxsplit:
                    current = text[i:]
                    break
            else:
                current += text[i]
                i += 1
    if current or not result:
        result.append(current)

    if in_string:
        raise SyntaxError('?-1:Expected \'"\'.')

    return result


