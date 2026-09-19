"""表达式树：求值 / 输出字符串（最小括号）/ 等价规范化（去重用）。"""

from fractions import Fraction
from utils import fraction_to_string

PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2}
DISPLAY    = {'+': '+', '-': '-', '*': '×', '/': '÷'}


class ExpressionNode:
    __slots__ = ('value', 'operator', 'left', 'right')

    def __init__(self, value=None, operator=None, left=None, right=None):
        self.value = value          # Fraction，叶子节点使用
        self.operator = operator    # '+','-','*','/'，内部节点使用
        self.left = left
        self.right = right

    # ---------- 基本属性 ----------
    def is_number(self) -> bool:
        return self.operator is None

    def operator_count(self) -> int:
        if self.is_number():
            return 0
        return 1 + self.left.operator_count() + self.right.operator_count()

    # ---------- 求值 ----------
    def evaluate(self) -> Fraction:
        if self.is_number():
            return self.value
        lv = self.left.evaluate()
        rv = self.right.evaluate()
        if self.operator == '+':
            return lv + rv
        if self.operator == '-':
            return lv - rv
        if self.operator == '*':
            return lv * rv
        if self.operator == '/':
            if rv == 0:
                raise ZeroDivisionError("除以零")
            return lv / rv
        raise ValueError(f"未知运算符: {self.operator}")

    # ---------- 输出（最小括号） ----------
    def to_string(self, parent_op=None, is_right=False) -> str:
        if self.is_number():
            return fraction_to_string(self.value)

        need_paren = False
        if parent_op is not None:
            my_p = PRECEDENCE[self.operator]
            pa_p = PRECEDENCE[parent_op]
            if my_p < pa_p:                                    # ① 优先级更低
                need_paren = True
            elif my_p == pa_p and is_right and parent_op in ('-', '/'):
                need_paren = True                              # ② 同级右孩子且父为 - 或 /

        left  = self.left.to_string(self.operator, is_right=False)
        right = self.right.to_string(self.operator, is_right=True)
        s = f"{left} {DISPLAY[self.operator]} {right}"
        return f"({s})" if need_paren else s

    # ---------- 等价规范化（用于去重） ----------
    def canonical(self) -> str:
        if self.is_number():
            return f"{self.value.numerator}/{self.value.denominator}"
        left = self.left.canonical()
        right = self.right.canonical()
        if self.operator in ('+', '*'):          # 仅 + 和 × 可交换
            if left > right:
                left, right = right, left
        return f"{self.operator}({left},{right})"