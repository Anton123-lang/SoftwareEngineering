"""递归下降解析器：把题目字符串还原为表达式树。"""

from expression import ExpressionNode
from utils import parse_number

OPERATOR_TOKENS = {'+', '-', '*', '/', '×', '÷'}


def tokenize(text: str):
    """切分 token：数字（含分数/带分数）、运算符、括号。"""
    tokens = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            if j < n and text[j] == "'":                # 带分数 2'3/8
                j += 1
                while j < n and text[j].isdigit():
                    j += 1
                if j < n and text[j] == '/':
                    j += 1
                    while j < n and text[j].isdigit():
                        j += 1
            elif j < n and text[j] == '/':              # 真分数 3/5
                k = j + 1
                while k < n and text[k].isdigit():
                    k += 1
                if k > j + 1:
                    j = k
            tokens.append(text[i:j])
            i = j
            continue
        if c in OPERATOR_TOKENS or c in '()':
            tokens.append(c)
            i += 1
            continue
        raise ValueError(f"无法识别的字符: {c!r}")
    return tokens


class ExpressionParser:
    def __init__(self, text: str):
        self.tokens = tokenize(text)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next_token(self):
        if self.pos >= len(self.tokens):
            raise ValueError("表达式意外结束")
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def parse(self) -> ExpressionNode:
        node = self.parse_expression()
        if not self.at_end():
            raise ValueError(f"表达式存在多余内容: {self.tokens[self.pos]!r}")
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.next_token()
            right = self.parse_term()
            node = ExpressionNode(operator=op, left=node, right=right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() in ('*', '/', '×', '÷'):
            op = self.next_token()
            op = {'×': '*', '÷': '/'}.get(op, op)
            right = self.parse_factor()
            node = ExpressionNode(operator=op, left=node, right=right)
        return node

    def parse_factor(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("表达式意外结束")
        if tok == '(':
            self.next_token()
            node = self.parse_expression()
            if self.peek() != ')':
                raise ValueError("缺少右括号")
            self.next_token()
            return node
        if tok in OPERATOR_TOKENS or tok == ')':
            raise ValueError(f"意外的符号: {tok!r}")
        self.next_token()
        return ExpressionNode(value=parse_number(tok))