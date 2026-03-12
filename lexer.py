import re
from enum import Enum, auto

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    NAME = auto()
    # Keywords
    AND = auto()
    BREAK = auto()
    DO = auto()
    ELSE = auto()
    ELSEIF = auto()
    END = auto()
    FALSE = auto()
    FOR = auto()
    FUNCTION = auto()
    GOTO = auto()
    IF = auto()
    IN = auto()
    LOCAL = auto()
    NIL = auto()
    NOT = auto()
    OR = auto()
    REPEAT = auto()
    RETURN = auto()
    THEN = auto()
    TRUE = auto()
    UNTIL = auto()
    WHILE = auto()
    # Symbols
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()
    HASH = auto()
    AMPERSAND = auto()
    TILDE = auto()
    PIPE = auto()
    LSHIFT = auto()
    RSHIFT = auto()
    DSLASH = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LEQ = auto()
    GEQ = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    DCOLON = auto()
    SEMICOLON = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    CONCAT = auto()
    DOTS = auto()
    ASSIGN = auto()
    # Special
    EOF = auto()
    COMMENT = auto()
    WHITESPACE = auto()

KEYWORDS = {
    'and': TokenType.AND, 'break': TokenType.BREAK, 'do': TokenType.DO,
    'else': TokenType.ELSE, 'elseif': TokenType.ELSEIF, 'end': TokenType.END,
    'false': TokenType.FALSE, 'for': TokenType.FOR, 'function': TokenType.FUNCTION,
    'goto': TokenType.GOTO, 'if': TokenType.IF, 'in': TokenType.IN,
    'local': TokenType.LOCAL, 'nil': TokenType.NIL, 'not': TokenType.NOT,
    'or': TokenType.OR, 'repeat': TokenType.REPEAT, 'return': TokenType.RETURN,
    'then': TokenType.THEN, 'true': TokenType.TRUE, 'until': TokenType.UNTIL,
    'while': TokenType.WHILE,
}

class Token:
    def __init__(self, type_, value, line=0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def error(self, msg):
        raise LexerError(f"Line {self.line}: {msg}")

    def peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else ''

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def match(self, expected):
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.pos += 1
            return True
        return False

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in ' \t\r\n':
                self.advance()
            elif ch == '-' and self.peek(1) == '-':
                self.pos += 2
                if self.peek() == '[':
                    level = self._check_long_bracket()
                    if level >= 0:
                        self._read_long_string(level)
                        continue
                while self.pos < len(self.source) and self.peek() != '\n':
                    self.pos += 1
            else:
                break

    def _check_long_bracket(self):
        if self.peek() != '[':
            return -1
        i = 1
        while self.peek(i) == '=':
            i += 1
        if self.peek(i) == '[':
            return i - 1
        return -1

    def _read_long_string(self, level):
        self.pos += 1  # skip [
        for _ in range(level):
            self.pos += 1  # skip =
        self.pos += 1  # skip [
        closing = ']' + '=' * level + ']'
        start = self.pos
        while self.pos < len(self.source):
            idx = self.source.find(closing, self.pos)
            if idx == -1:
                self.error("unfinished long string")
            content = self.source[start:idx]
            self.line += content.count('\n')
            self.pos = idx + len(closing)
            return content
        self.error("unfinished long string")

    def read_string(self, quote):
        self.advance()  # skip opening quote
        result = []
        while self.pos < len(self.source):
            ch = self.peek()
            if ch == quote:
                self.advance()
                return ''.join(result)
            elif ch == '\\':
                self.advance()
                esc = self.advance()
                escapes = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                           "'": "'", '"': '"', 'a': '\a', 'b': '\b',
                           'f': '\f', 'v': '\v', '0': '\0'}
                if esc in escapes:
                    result.append(escapes[esc])
                elif esc == '\n' or esc == '\r':
                    result.append('\n')
                elif esc.isdigit():
                    num = esc
                    for _ in range(2):
                        if self.peek().isdigit():
                            num += self.advance()
                    result.append(chr(int(num)))
                else:
                    result.append('\\')
                    result.append(esc)
            elif ch == '\n' or ch == '\r':
                self.error("unfinished string")
            else:
                result.append(self.advance())
        self.error("unfinished string")

    def read_number(self):
        start = self.pos
        if self.peek() == '0' and self.peek(1) in 'xX':
            self.pos += 2
            while self.peek() in '0123456789abcdefABCDEF_':
                self.pos += 1
        else:
            while self.peek().isdigit() or self.peek() == '_':
                self.pos += 1
            if self.peek() == '.' and self.peek(1) != '.':
                self.pos += 1
                while self.peek().isdigit():
                    self.pos += 1
            if self.peek() in 'eE':
                self.pos += 1
                if self.peek() in '+-':
                    self.pos += 1
                while self.peek().isdigit():
                    self.pos += 1
        return self.source[start:self.pos]

    def tokenize(self):
        tokens = []
        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                tokens.append(Token(TokenType.EOF, '', self.line))
                break

            line = self.line
            ch = self.peek()

            # String
            if ch in ('"', "'"):
                val = self.read_string(ch)
                tokens.append(Token(TokenType.STRING, val, line))
                continue

            # Long string
            if ch == '[':
                level = self._check_long_bracket()
                if level >= 0:
                    val = self._read_long_string(level)
                    tokens.append(Token(TokenType.STRING, val, line))
                    continue

            # Number
            if ch.isdigit() or (ch == '.' and self.peek(1).isdigit()):
                val = self.read_number()
                tokens.append(Token(TokenType.NUMBER, val, line))
                continue

            # Name / Keyword
            if ch.isalpha() or ch == '_':
                start = self.pos
                while self.peek().isalnum() or self.peek() == '_':
                    self.pos += 1
                word = self.source[start:self.pos]
                ttype = KEYWORDS.get(word, TokenType.NAME)
                tokens.append(Token(ttype, word, line))
                continue

            # Symbols
            self.pos += 1
            if ch == '+': tokens.append(Token(TokenType.PLUS, '+', line))
            elif ch == '*': tokens.append(Token(TokenType.STAR, '*', line))
            elif ch == '%': tokens.append(Token(TokenType.PERCENT, '%', line))
            elif ch == '^': tokens.append(Token(TokenType.CARET, '^', line))
            elif ch == '#': tokens.append(Token(TokenType.HASH, '#', line))
            elif ch == '&': tokens.append(Token(TokenType.AMPERSAND, '&', line))
            elif ch == '|': tokens.append(Token(TokenType.PIPE, '|', line))
            elif ch == '(': tokens.append(Token(TokenType.LPAREN, '(', line))
            elif ch == ')': tokens.append(Token(TokenType.RPAREN, ')', line))
            elif ch == '{': tokens.append(Token(TokenType.LBRACE, '{', line))
            elif ch == '}': tokens.append(Token(TokenType.RBRACE, '}', line))
            elif ch == ']': tokens.append(Token(TokenType.RBRACKET, ']', line))
            elif ch == '[': tokens.append(Token(TokenType.LBRACKET, '[', line))
            elif ch == ';': tokens.append(Token(TokenType.SEMICOLON, ';', line))
            elif ch == ',': tokens.append(Token(TokenType.COMMA, ',', line))
            elif ch == '-': tokens.append(Token(TokenType.MINUS, '-', line))
            elif ch == '/':
                if self.match('/'):
                    tokens.append(Token(TokenType.DSLASH, '//', line))
                else:
                    tokens.append(Token(TokenType.SLASH, '/', line))
            elif ch == '~':
                if self.match('='):
                    tokens.append(Token(TokenType.NEQ, '~=', line))
                else:
                    tokens.append(Token(TokenType.TILDE, '~', line))
            elif ch == '<':
                if self.match('<'):
                    tokens.append(Token(TokenType.LSHIFT, '<<', line))
                elif self.match('='):
                    tokens.append(Token(TokenType.LEQ, '<=', line))
                else:
                    tokens.append(Token(TokenType.LT, '<', line))
            elif ch == '>':
                if self.match('>'):
                    tokens.append(Token(TokenType.RSHIFT, '>>', line))
                elif self.match('='):
                    tokens.append(Token(TokenType.GEQ, '>=', line))
                else:
                    tokens.append(Token(TokenType.GT, '>', line))
            elif ch == '=':
                if self.match('='):
                    tokens.append(Token(TokenType.EQ, '==', line))
                else:
                    tokens.append(Token(TokenType.ASSIGN, '=', line))
            elif ch == ':':
                if self.match(':'):
                    tokens.append(Token(TokenType.DCOLON, '::', line))
                else:
                    tokens.append(Token(TokenType.COLON, ':', line))
            elif ch == '.':
                if self.match('.'):
                    if self.match('.'):
                        tokens.append(Token(TokenType.DOTS, '...', line))
                    else:
                        tokens.append(Token(TokenType.CONCAT, '..', line))
                else:
                    tokens.append(Token(TokenType.DOT, '.', line))
            else:
                self.error(f"Unexpected character: {ch!r}")

        return tokens
