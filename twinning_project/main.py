"""命令行入口。

生成模式：  python main.py -n 10 -r 10
批改模式：  python main.py -e Exercises.txt -a Answers.txt
图形界面：  python main.py -g
"""

import argparse
import sys

from generator import generate_exercises
from grader import grade
from utils import save_lines, fraction_to_string


def build_parser():
    p = argparse.ArgumentParser(
        prog='Myapp.exe',
        description='小学四则运算题目自动生成 / 批改程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '示例:\n'
            '  Myapp.exe -n 10 -r 10                      生成 10 道题\n'
            '  Myapp.exe -r 20                            默认生成 10 道题\n'
            '  Myapp.exe -e Exercises.txt -a Answers.txt  批改\n'
        ),
    )
    p.add_argument('-n', type=int, default=10, help='生成题目的个数（默认 10）')
    p.add_argument('-r', type=int, default=None,
                   help='题目中数值（自然数、真分数、分母）的范围，必须给定')
    p.add_argument('-e', metavar='<exercisefile>.txt', default=None, help='待批改的题目文件')
    p.add_argument('-a', metavar='<answerfile>.txt', default=None, help='待批改的答案文件')
    p.add_argument('-g', '--gui', action='store_true', help='启动图形界面')
    return p


def run_generate(args, parser) -> int:
    if args.r is None:
        print('错误：生成题目时必须使用 -r 参数指定数值范围。', file=sys.stderr)
        parser.print_help()
        return 1
    if args.r < 1:
        print('错误：-r 必须是不小于 1 的自然数。', file=sys.stderr)
        return 1
    if args.n < 0:
        print('错误：-n 必须是非负整数。', file=sys.stderr)
        return 1

    try:
        exercises = generate_exercises(args.n, args.r)
    except (ValueError, RuntimeError) as e:
        print(f'错误：{e}', file=sys.stderr)
        return 1

    save_lines('Exercises.txt', [ex.text() for ex in exercises])
    save_lines('Answers.txt', [fraction_to_string(ex.answer) for ex in exercises])
    print(f'已生成 {len(exercises)} 道题目 -> Exercises.txt')
    print('对应答案已写入 -> Answers.txt')
    return 0


def run_grade(args, parser) -> int:
    if not (args.e and args.a):
        print('错误：批改模式必须同时提供 -e 与 -a 参数。', file=sys.stderr)
        parser.print_help()
        return 1
    try:
        correct, wrong = grade(args.e, args.a)
    except FileNotFoundError as e:
        print(f'错误：找不到文件 {e.filename}', file=sys.stderr)
        return 1

    print(f"Correct: {len(correct)} ({', '.join(map(str, correct))})")
    print(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})")
    print('统计结果已写入 -> Grade.txt')
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui:
        from gui import launch
        launch()
        return 0

    if args.e or args.a:
        return run_grade(args, parser)
    return run_generate(args, parser)


if __name__ == '__main__':
    sys.exit(main())