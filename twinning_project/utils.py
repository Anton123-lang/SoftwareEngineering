"""通用工具：分数与字符串互转、文件读写。"""

from fractions import Fraction


def fraction_to_string(value: Fraction) -> str:
    """把 Fraction 转成题目要求的显示格式。

    整数      ->  "3"
    真分数    ->  "3/5"
    带分数    ->  "1'3/8"
    负带分数  ->  "-1'3/8"
    """
    n, d = value.numerator, value.denominator
    if d == 1:                       # 整数
        return str(n)
    if abs(n) < d:                   # 真分数
        return f"{n}/{d}"
    sign = "-" if n < 0 else ""      # 带分数
    a = abs(n)
    return f"{sign}{a // d}'{a % d}/{d}"


def parse_number(text: str) -> Fraction:
    """把 "3" / "3/5" / "2'3/8" / "-1'3/8" 解析为 Fraction。"""
    s = text.strip()
    if not s:
        raise ValueError("空数字")
    sign = 1
    if s[0] in '+-':
        if s[0] == '-':
            sign = -1
        s = s[1:]
    if "'" in s:
        whole, frac = s.split("'", 1)
        num, den = frac.split('/')
        value = Fraction(int(whole)) + Fraction(int(num), int(den))
    elif '/' in s:
        num, den = s.split('/', 1)
        value = Fraction(int(num), int(den))
    else:
        value = Fraction(int(s))
    return sign * value


def save_lines(path: str, lines) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


def read_lines(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return [ln.rstrip('\n') for ln in f if ln.strip()]