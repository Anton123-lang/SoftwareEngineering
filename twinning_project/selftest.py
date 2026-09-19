"""一键自测：验证核心逻辑是否全部正确。"""
from fractions import Fraction
from utils import fraction_to_string, parse_number
from expr_parser import ExpressionParser
from generator import generate_exercises

passed = 0
failed = []

def check(name, got, want):
    global passed
    if got == want:
        print(f"[PASS] {name}")
        passed += 1
    else:
        msg = f"[FAIL] {name}: got {got!r}, want {want!r}"
        print(msg)
        failed.append(msg)

# ---------- T01 分数格式转换 ----------
check("T01-1", fraction_to_string(Fraction(3, 5)),  "3/5")
check("T01-2", fraction_to_string(Fraction(8, 4)),  "2")
check("T01-3", fraction_to_string(Fraction(11, 8)), "1'3/8")
check("T01-4", fraction_to_string(Fraction(-11, 8)),"-1'3/8")

# ---------- T02 数字解析 ----------
check("T02-1", parse_number("3"),      Fraction(3))
check("T02-2", parse_number("3/5"),    Fraction(3, 5))
check("T02-3", parse_number("2'3/8"),  Fraction(19, 8))

# ---------- T04 基本计算 ----------
check("T04-1", ExpressionParser("3 + 5").parse().evaluate(),     Fraction(8))
check("T04-2", ExpressionParser("1/6 + 1/8").parse().evaluate(), Fraction(7, 24))

# ---------- T05 优先级 ----------
check("T05-1", ExpressionParser("3 + 5 × 2").parse().evaluate(),   Fraction(13))
check("T05-2", ExpressionParser("(3 + 5) × 2").parse().evaluate(), Fraction(16))

# ---------- T06 左结合 ----------
check("T06-1", ExpressionParser("8 - 3 - 1").parse().evaluate(), Fraction(4))
check("T06-2", ExpressionParser("8 ÷ 4 ÷ 2").parse().evaluate(), Fraction(1))

# ---------- T07 交换律去重 ----------
c1 = ExpressionParser("3 + 5").parse().canonical()
c2 = ExpressionParser("5 + 3").parse().canonical()
check("T07", c1 == c2, True)

# ---------- T08 结合律去重 ----------
c3 = ExpressionParser("3 + (2 + 1)").parse().canonical()
c4 = ExpressionParser("1 + 2 + 3").parse().canonical()
c5 = ExpressionParser("3 + 2 + 1").parse().canonical()
check("T08-1", c3 == c4, True)
check("T08-2", c4 == c5, False)

# ---------- T09~T13 随机约束与去重 ----------
exs = generate_exercises(300, 10)
check("T09-数量", len(exs), 300)
check("T11-去重", len({e.canonical() for e in exs}), 300)
all_ok = all(e.root.operator_count() <= 3 and e.answer >= 0 for e in exs)
check("T10-约束", all_ok, True)

# 闭环：题目字符串 -> 重新解析 -> 结果与生成时答案一致
closed_ok = True
for e in exs:
    text = e.text().rstrip('=').strip()
    if ExpressionParser(text).parse().evaluate() != e.answer:
        closed_ok = False
        break
check("T13-闭环", closed_ok, True)

# ---------- 结果 ----------
print(f"\n通过 {passed} / {passed + len(failed)}")
if failed:
    for m in failed:
        print(" ", m)
else:
    print("全部通过 ✔")