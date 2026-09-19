"""题目生成：随机生成 + 合法性约束 + 去重。"""

import random
from fractions import Fraction

from expression import ExpressionNode

OPERATORS = ['+', '-', '*', '/']


class Exercise:
    """一道四则运算题。"""

    def __init__(self, root: ExpressionNode, answer: Fraction):
        self.root = root
        self.answer = answer

    def text(self) -> str:
        return f"{self.root.to_string()} ="

    def canonical(self) -> str:
        return self.root.canonical()


# ---------------------- 单个数值 ----------------------

def generate_number(r: int):
    """生成一个自然数或真分数，所有数值（含分母）都在 [1, r) 内。"""
    if r <= 1:
        return None
    if r == 2:
        return Fraction(1, 1)
    if random.random() < 0.5:                       # 自然数
        return Fraction(random.randint(1, r - 1), 1)
    den = random.randint(2, r - 1)                  # 真分数
    num = random.randint(1, den - 1)
    return Fraction(num, den)


# ---------------------- 表达式树 ----------------------

def _build(operator_count: int, r: int):
    """递归生成一棵运算符数量为 operator_count 的合法表达式树。"""
    if operator_count == 0:
        v = generate_number(r)
        if v is None:
            return None
        return ExpressionNode(value=v)

    for _ in range(80):
        op = random.choice(OPERATORS)
        remaining = operator_count - 1
        left_count = random.randint(0, remaining)
        right_count = remaining - left_count

        left = _build(left_count, r)
        right = _build(right_count, r)
        if left is None or right is None:
            continue

        lv = left.evaluate()
        rv = right.evaluate()

        if op == '-':
            # 保证 e1 >= e2（不产生负数）
            if lv < rv:
                left, right = right, left
                lv, rv = rv, lv
        elif op == '/':
            if rv == 0 or lv == 0:
                continue
            # 保证 e1 / e2 是真分数，即 e1 < e2
            if lv >= rv:
                left, right = right, left
                lv, rv = rv, lv
            if lv >= rv:
                continue

        return ExpressionNode(operator=op, left=left, right=right)

    return None


# ---------------------- 批量生成 ----------------------

def generate_exercises(n: int, r: int, max_operators: int = 3):
    """生成 n 道互不重复的题目。"""
    if r < 2:
        raise ValueError(f"r={r} 太小，无法生成题目（至少需要 r >= 2）。")

    seen = set()
    exercises = []
    attempts = 0
    limit = max(2000, n * 400)

    while len(exercises) < n and attempts < limit:
        attempts += 1
        k = random.randint(1, max_operators)
        root = _build(k, r)
        if root is None:
            continue
        canon = root.canonical()
        if canon in seen:
            continue
        seen.add(canon)
        exercises.append(Exercise(root, root.evaluate()))

    if len(exercises) < n:
        raise RuntimeError(
            f"在 r={r} 的范围内无法生成 {n} 道互不重复的题目，"
            f"实际生成 {len(exercises)} 道。请增大 -r 或减小 -n。"
        )
    return exercises