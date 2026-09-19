"""批改：对题目文件与答案文件进行对错判定与统计。"""

from expr_parser import ExpressionParser
from utils import parse_number, save_lines, read_lines


def evaluate_exercise(text: str):
    """解析并计算一行题目（形如 "3 + 5 × 2 ="）。"""
    s = text.strip()
    if s.endswith('='):
        s = s[:-1].strip()
    return ExpressionParser(s).parse().evaluate()


def grade(exercise_file: str, answer_file: str, output_file: str = 'Grade.txt'):
    exercises = read_lines(exercise_file)
    answers = read_lines(answer_file)

    correct, wrong = [], []
    total = max(len(exercises), len(answers))

    for i in range(total):
        no = i + 1
        ok = False
        if i < len(exercises) and i < len(answers):
            try:
                expected = evaluate_exercise(exercises[i])
                given = parse_number(answers[i])
                ok = (expected == given)
            except Exception:
                ok = False
        (correct if ok else wrong).append(no)

    lines = [
        f"Correct: {len(correct)} ({', '.join(map(str, correct))})",
        f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})",
    ]
    save_lines(output_file, lines)
    return correct, wrong