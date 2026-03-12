from lexer import TokenType, Token

class ParseError(Exception):
    pass

# AST Node classes
class Node:
    pass

class Block(Node):
    def __init__(self, stmts, ret=None):
        self.stmts = stmts
        self.ret = ret

class AssignStmt(Node):
    def __init__(self, targets, values):
        self.targets = targets
        self.values = values

class LocalStmt(Node):
    def __init__(self, names, attribs, values):
        self.names = names
        self.attribs = attribs
        self.values = values

class DoStmt(Node):
    def __init__(self, block):
        self.block = block

class WhileStmt(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block

class RepeatStmt(Node):
    def __init__(self, block, cond):
        self.block = block
        self.cond = cond

class IfStmt(Node):
    def __init__(self, cond, then_block, elseifs, else_block):
        self.cond = cond
        self.then_block = then_block
        self.elseifs = elseifs
        self.else_block = else_block

class ForNumStmt(Node):
    def __init__(self, name, start, stop, step, block):
        self.name = name
        self.start = start
        self.stop = stop
        self.step = step
        self.block = block

class ForInStmt(Node):
    def __init__(self, names, iters, block):
        self.names = names
        self.iters = iters
        self.block = block

class FuncStmt(Node):
    def __init__(self, name, method, params, has_vararg, block):
        self.name = name
        self.method = method
        self.params = params
        self.has_vararg = has_vararg
        self.block = block

class LocalFuncStmt(Node):
    def __init__(self, name, params, has_vararg, block):
        self.name = name
        self.params = params
        self.has_vararg = has_vararg
        self.block = block

class ReturnStmt(Node):
    def __init__(self, values):
        self.values = values

class BreakStmt(Node):
    pass

class GotoStmt(Node):
    def __init__(self, label):
        self.label = label

class LabelStmt(Node):
    def __init__(self, name):
        self.name = name

class CallStmt(Node):
    def __init__(self, expr):
        self.expr = expr

# Expressions
class NameExpr(Node):
    def __init__(self, name):
        self.name = name

class NumberExpr(Node):
    def __init__(self, value):
        self.value = value

class StringExpr(Node):
    def __init__(self, value):
        self.value = value

class BoolExpr(Node):
    def __init__(self, value):
        self.value = value

class NilExpr(Node):
    pass

class VarArgExpr(Node):
    pass

class BinOpExpr(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnOpExpr(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class IndexExpr(Node):
    def __init__(self, table, key):
        self.table = table
        self.key = key

class FieldExpr(Node):
    def __init__(self, table, field):
        self.table = table
        self.field = field

class MethodCallExpr(Node):
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args

class CallExpr(Node):
    def __init__(self, func, args):
        self.func = func
        self.args = args

class FuncExpr(Node):
    def __init__(self, params, has_vararg, block):
        self.params = params
        self.has_vararg = has_vararg
        self.block = block

class TableExpr(Node):
    def __init__(self, fields):
        self.fields = fields

class TableField(Node):
    def __init__(self, key, value):
        self.key = key
        self.value = value


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def error(self, msg):
        tok = self.current()
        raise ParseError(f"Line {tok.line}: {msg} (got {tok.type} {tok.value!r})")

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else self.tokens[-1]

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def check(self, *types):
        return self.current().type in types

    def match(self, *types):
        if self.current().type in types:
            return self.advance()
        return None

    def expect(self, type_, msg=None):
        if self.current().type == type_:
            return self.advance()
        self.error(msg or f"expected {type_}")

    def parse(self):
        block = self.parse_block()
        self.expect(TokenType.EOF)
        return block

    def parse_block(self):
        stmts = []
        ret = None
        while True:
            while self.match(TokenType.SEMICOLON):
                pass
            if self.check(TokenType.EOF, TokenType.END, TokenType.ELSE,
                          TokenType.ELSEIF, TokenType.UNTIL):
                break
            if self.check(TokenType.RETURN):
                ret = self.parse_return()
                self.match(TokenType.SEMICOLON)
                break
            stmt = self.parse_stmt()
            if stmt:
                stmts.append(stmt)
        return Block(stmts, ret)

    def parse_return(self):
        self.expect(TokenType.RETURN)
        values = []
        if not self.check(TokenType.EOF, TokenType.END, TokenType.ELSE,
                          TokenType.ELSEIF, TokenType.UNTIL, TokenType.SEMICOLON):
            values = self.parse_expr_list()
        return ReturnStmt(values)

    def parse_stmt(self):
        tok = self.current()

        if tok.type == TokenType.IF:
            return self.parse_if()
        elif tok.type == TokenType.WHILE:
            return self.parse_while()
        elif tok.type == TokenType.DO:
            return self.parse_do()
        elif tok.type == TokenType.FOR:
            return self.parse_for()
        elif tok.type == TokenType.REPEAT:
            return self.parse_repeat()
        elif tok.type == TokenType.FUNCTION:
            return self.parse_func_stmt()
        elif tok.type == TokenType.LOCAL:
            return self.parse_local()
        elif tok.type == TokenType.GOTO:
            self.advance()
            name = self.expect(TokenType.NAME).value
            return GotoStmt(name)
        elif tok.type == TokenType.BREAK:
            self.advance()
            return BreakStmt()
        elif tok.type == TokenType.DCOLON:
            self.advance()
            name = self.expect(TokenType.NAME).value
            self.expect(TokenType.DCOLON)
            return LabelStmt(name)
        else:
            return self.parse_expr_stmt()

    def parse_if(self):
        self.expect(TokenType.IF)
        cond = self.parse_expr()
        self.expect(TokenType.THEN)
        then_block = self.parse_block()
        elseifs = []
        else_block = None
        while self.check(TokenType.ELSEIF):
            self.advance()
            ec = self.parse_expr()
            self.expect(TokenType.THEN)
            eb = self.parse_block()
            elseifs.append((ec, eb))
        if self.match(TokenType.ELSE):
            else_block = self.parse_block()
        self.expect(TokenType.END)
        return IfStmt(cond, then_block, elseifs, else_block)

    def parse_while(self):
        self.expect(TokenType.WHILE)
        cond = self.parse_expr()
        self.expect(TokenType.DO)
        block = self.parse_block()
        self.expect(TokenType.END)
        return WhileStmt(cond, block)

    def parse_do(self):
        self.expect(TokenType.DO)
        block = self.parse_block()
        self.expect(TokenType.END)
        return DoStmt(block)

    def parse_repeat(self):
        self.expect(TokenType.REPEAT)
        block = self.parse_block()
        self.expect(TokenType.UNTIL)
        cond = self.parse_expr()
        return RepeatStmt(block, cond)

    def parse_for(self):
        self.expect(TokenType.FOR)
        name = self.expect(TokenType.NAME).value
        if self.match(TokenType.ASSIGN):
            start = self.parse_expr()
            self.expect(TokenType.COMMA)
            stop = self.parse_expr()
            step = None
            if self.match(TokenType.COMMA):
                step = self.parse_expr()
            self.expect(TokenType.DO)
            block = self.parse_block()
            self.expect(TokenType.END)
            return ForNumStmt(name, start, stop, step, block)
        else:
            names = [name]
            while self.match(TokenType.COMMA):
                names.append(self.expect(TokenType.NAME).value)
            self.expect(TokenType.IN)
            iters = self.parse_expr_list()
            self.expect(TokenType.DO)
            block = self.parse_block()
            self.expect(TokenType.END)
            return ForInStmt(names, iters, block)

    def parse_func_stmt(self):
        self.expect(TokenType.FUNCTION)
        name = [self.expect(TokenType.NAME).value]
        while self.match(TokenType.DOT):
            name.append(self.expect(TokenType.NAME).value)
        method = None
        if self.match(TokenType.COLON):
            method = self.expect(TokenType.NAME).value
        params, has_vararg = self.parse_func_params()
        block = self.parse_block()
        self.expect(TokenType.END)
        return FuncStmt(name, method, params, has_vararg, block)

    def parse_local(self):
        self.expect(TokenType.LOCAL)
        if self.match(TokenType.FUNCTION):
            name = self.expect(TokenType.NAME).value
            params, has_vararg = self.parse_func_params()
            block = self.parse_block()
            self.expect(TokenType.END)
            return LocalFuncStmt(name, params, has_vararg, block)
        else:
            names = [self.expect(TokenType.NAME).value]
            attribs = [self._parse_attrib()]
            while self.match(TokenType.COMMA):
                names.append(self.expect(TokenType.NAME).value)
                attribs.append(self._parse_attrib())
            values = []
            if self.match(TokenType.ASSIGN):
                values = self.parse_expr_list()
            return LocalStmt(names, attribs, values)

    def _parse_attrib(self):
        if self.match(TokenType.LT):
            name = self.expect(TokenType.NAME).value
            self.expect(TokenType.GT)
            return name
        return None

    def parse_func_params(self):
        self.expect(TokenType.LPAREN)
        params = []
        has_vararg = False
        if not self.check(TokenType.RPAREN):
            if self.match(TokenType.DOTS):
                has_vararg = True
            else:
                params.append(self.expect(TokenType.NAME).value)
                while self.match(TokenType.COMMA):
                    if self.match(TokenType.DOTS):
                        has_vararg = True
                        break
                    params.append(self.expect(TokenType.NAME).value)
        self.expect(TokenType.RPAREN)
        return params, has_vararg

    def parse_expr_stmt(self):
        expr = self.parse_suffixed_expr()
        if self.check(TokenType.ASSIGN, TokenType.COMMA):
            targets = [expr]
            while self.match(TokenType.COMMA):
                targets.append(self.parse_suffixed_expr())
            self.expect(TokenType.ASSIGN)
            values = self.parse_expr_list()
            return AssignStmt(targets, values)
        if isinstance(expr, (CallExpr, MethodCallExpr)):
            return CallStmt(expr)
        self.error("syntax error near expression")

    def parse_expr_list(self):
        exprs = [self.parse_expr()]
        while self.match(TokenType.COMMA):
            exprs.append(self.parse_expr())
        return exprs

    def parse_expr(self):
        return self.parse_or_expr()

    def parse_or_expr(self):
        left = self.parse_and_expr()
        while self.check(TokenType.OR):
            op = self.advance().value
            right = self.parse_and_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_and_expr(self):
        left = self.parse_cmp_expr()
        while self.check(TokenType.AND):
            op = self.advance().value
            right = self.parse_cmp_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_cmp_expr(self):
        left = self.parse_bitor_expr()
        while self.check(TokenType.LT, TokenType.GT, TokenType.LEQ,
                         TokenType.GEQ, TokenType.EQ, TokenType.NEQ):
            op = self.advance().value
            right = self.parse_bitor_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_bitor_expr(self):
        left = self.parse_bitxor_expr()
        while self.check(TokenType.PIPE):
            op = self.advance().value
            right = self.parse_bitxor_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_bitxor_expr(self):
        left = self.parse_bitand_expr()
        while self.check(TokenType.TILDE):
            op = self.advance().value
            right = self.parse_bitand_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_bitand_expr(self):
        left = self.parse_shift_expr()
        while self.check(TokenType.AMPERSAND):
            op = self.advance().value
            right = self.parse_shift_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_shift_expr(self):
        left = self.parse_concat_expr()
        while self.check(TokenType.LSHIFT, TokenType.RSHIFT):
            op = self.advance().value
            right = self.parse_concat_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_concat_expr(self):
        left = self.parse_add_expr()
        if self.check(TokenType.CONCAT):
            op = self.advance().value
            right = self.parse_concat_expr()
            return BinOpExpr(op, left, right)
        return left

    def parse_add_expr(self):
        left = self.parse_mul_expr()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_mul_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_mul_expr(self):
        left = self.parse_unary_expr()
        while self.check(TokenType.STAR, TokenType.SLASH,
                         TokenType.DSLASH, TokenType.PERCENT):
            op = self.advance().value
            right = self.parse_unary_expr()
            left = BinOpExpr(op, left, right)
        return left

    def parse_unary_expr(self):
        if self.check(TokenType.NOT):
            op = self.advance().value
            return UnOpExpr(op, self.parse_unary_expr())
        if self.check(TokenType.MINUS):
            op = self.advance().value
            return UnOpExpr('-', self.parse_unary_expr())
        if self.check(TokenType.HASH):
            op = self.advance().value
            return UnOpExpr('#', self.parse_unary_expr())
        if self.check(TokenType.TILDE):
            op = self.advance().value
            return UnOpExpr('~', self.parse_unary_expr())
        return self.parse_power_expr()

    def parse_power_expr(self):
        base = self.parse_suffixed_expr()
        if self.check(TokenType.CARET):
            op = self.advance().value
            exp = self.parse_unary_expr()
            return BinOpExpr(op, base, exp)
        return base

    def parse_suffixed_expr(self):
        expr = self.parse_primary_expr()
        while True:
            if self.check(TokenType.DOT):
                self.advance()
                field = self.expect(TokenType.NAME).value
                expr = FieldExpr(expr, field)
            elif self.check(TokenType.LBRACKET):
                self.advance()
                key = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                expr = IndexExpr(expr, key)
            elif self.check(TokenType.COLON):
                self.advance()
                method = self.expect(TokenType.NAME).value
                args = self.parse_call_args()
                expr = MethodCallExpr(expr, method, args)
            elif self.check(TokenType.LPAREN, TokenType.LBRACE, TokenType.STRING):
                args = self.parse_call_args()
                expr = CallExpr(expr, args)
            else:
                break
        return expr

    def parse_call_args(self):
        if self.check(TokenType.LPAREN):
            self.advance()
            args = []
            if not self.check(TokenType.RPAREN):
                args = self.parse_expr_list()
            self.expect(TokenType.RPAREN)
            return args
        elif self.check(TokenType.LBRACE):
            return [self.parse_table()]
        elif self.check(TokenType.STRING):
            val = self.advance().value
            return [StringExpr(val)]
        self.error("expected function arguments")

    def parse_primary_expr(self):
        tok = self.current()
        if tok.type == TokenType.NAME:
            self.advance()
            return NameExpr(tok.value)
        elif tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr
        elif tok.type == TokenType.NUMBER:
            self.advance()
            return NumberExpr(tok.value)
        elif tok.type == TokenType.STRING:
            self.advance()
            return StringExpr(tok.value)
        elif tok.type == TokenType.TRUE:
            self.advance()
            return BoolExpr(True)
        elif tok.type == TokenType.FALSE:
            self.advance()
            return BoolExpr(False)
        elif tok.type == TokenType.NIL:
            self.advance()
            return NilExpr()
        elif tok.type == TokenType.DOTS:
            self.advance()
            return VarArgExpr()
        elif tok.type == TokenType.FUNCTION:
            self.advance()
            params, has_vararg = self.parse_func_params()
            block = self.parse_block()
            self.expect(TokenType.END)
            return FuncExpr(params, has_vararg, block)
        elif tok.type == TokenType.LBRACE:
            return self.parse_table()
        self.error(f"unexpected symbol near {tok.value!r}")

    def parse_table(self):
        self.expect(TokenType.LBRACE)
        fields = []
        while not self.check(TokenType.RBRACE):
            if self.check(TokenType.LBRACKET):
                self.advance()
                key = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.ASSIGN)
                val = self.parse_expr()
                fields.append(TableField(key, val))
            elif self.check(TokenType.NAME) and self.peek().type == TokenType.ASSIGN:
                key = StringExpr(self.advance().value)
                self.advance()
                val = self.parse_expr()
                fields.append(TableField(key, val))
            else:
                val = self.parse_expr()
                fields.append(TableField(None, val))
            if not self.match(TokenType.COMMA, TokenType.SEMICOLON):
                break
        self.expect(TokenType.RBRACE)
        return TableExpr(fields)
