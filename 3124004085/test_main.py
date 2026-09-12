"""
论文查重程序单元测试
覆盖：正常/边界/异常/参数解析/结果输出/main 入口
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from main import (
    read_file, segment, build_word_freq, cosine_similarity,
    compute_similarity, parse_arguments, write_result,
    main, FileEncodingError,
)


class TestPaperCheck(unittest.TestCase):
    """核心查重功能测试"""

    def setUp(self):
        """初始化测试用文本"""
        self.orig_text = "今天是星期天，天气晴，今天晚上我要去看电影。"
        self.copy_text = "今天是周天，天气晴朗，我晚上要去看电影。"

    def test_identical_text(self):
        """完全相同文本，相似度应为 1.0"""
        freq1 = build_word_freq(segment(self.orig_text))
        freq2 = build_word_freq(segment(self.orig_text))
        self.assertAlmostEqual(cosine_similarity(freq1, freq2), 1.0, places=2)

    def test_partial_copy(self):
        """部分抄袭文本，相似度应大于 0.5"""
        sim = compute_similarity(self.orig_text, self.copy_text)
        self.assertGreater(sim, 0.5)

    def test_special_chars(self):
        """含中英文数字符号的文本应正确分词"""
        words = segment("Hello，世界！2023年...")
        self.assertIn("世界", words)
        self.assertIn("2023", words)

    def test_punctuation_filtered(self):
        """纯标点符号应被完全过滤"""
        words = segment("！！！，，。？？？")
        self.assertEqual(words, [])

    def test_number_kept(self):
        """数字应被保留为词语"""
        words = segment("2023年是一个好年份")
        self.assertIn("2023", words)

    def test_unrelated_text(self):
        """完全无关文本相似度应较低"""
        sim = compute_similarity("苹果香蕉橘子", "汽车飞机轮船")
        self.assertLess(sim, 0.3)

    def test_long_text(self):
        """长文本自身相似度应为 1.0"""
        text = "人工智能技术正在快速发展。" * 50
        sim = compute_similarity(text, text)
        self.assertAlmostEqual(sim, 1.0, places=2)

    def test_output_format(self):
        """结果应保留两位小数"""
        sim = compute_similarity(self.orig_text, self.copy_text)
        self.assertEqual(len(f"{sim:.2f}".split('.')[1]), 2)


class TestEdgeCases(unittest.TestCase):
    """边界与异常处理测试"""

    def test_empty_orig(self):
        """空原文相似度应为 0.0"""
        self.assertEqual(compute_similarity("", "测试文本"), 0.0)

    def test_empty_copy(self):
        """空抄袭文相似度应为 0.0"""
        self.assertEqual(compute_similarity("测试文本", ""), 0.0)

    def test_both_empty(self):
        """两者都空相似度应为 0.0"""
        self.assertEqual(compute_similarity("", ""), 0.0)

    def test_short_text(self):
        """单字文本相似度应为 0.0"""
        self.assertEqual(compute_similarity("我", "你"), 0.0)

    def test_file_not_found(self):
        """文件不存在应抛 FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            read_file("non_exist_file_xyz.txt")

    def test_encoding_error(self):
        """非 UTF-8 文件应抛 FileEncodingError"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as file:
            file.write(b'\xff\xfe')
            file.close()
            try:
                with self.assertRaises(FileEncodingError):
                    read_file(file.name)
            finally:
                os.unlink(file.name)

    def test_parse_arguments_ok(self):
        """参数数量正确时应返回三元组"""
        result = parse_arguments(["main.py", "a.txt", "b.txt", "c.txt"])
        self.assertEqual(result, ("a.txt", "b.txt", "c.txt"))

    def test_parse_arguments_error(self):
        """参数数量错误应抛 ValueError"""
        with self.assertRaises(ValueError):
            parse_arguments(["main.py", "a.txt"])

    def test_write_result(self):
        """写出结果应四舍五入到两位小数"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as file:
            file.close()
            try:
                write_result(file.name, 0.8456)
                with open(file.name, 'r', encoding='utf-8') as fp:
                    self.assertEqual(fp.read(), "0.85")
            finally:
                os.unlink(file.name)

    def test_write_result_zero(self):
        """相似度为 0 时应输出 0.00"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as file:
            file.close()
            try:
                write_result(file.name, 0.0)
                with open(file.name, 'r', encoding='utf-8') as fp:
                    self.assertEqual(fp.read(), "0.00")
            finally:
                os.unlink(file.name)


class TestMainEntry(unittest.TestCase):
    """main() 入口函数测试"""

    def test_main_success(self):
        """参数正确时应正常执行并写出结果"""
        with tempfile.TemporaryDirectory() as tmp:
            orig = os.path.join(tmp, "o.txt")
            copy = os.path.join(tmp, "c.txt")
            ans = os.path.join(tmp, "a.txt")
            with open(orig, "w", encoding="utf-8") as file:
                file.write("人工智能技术正在快速发展")
            with open(copy, "w", encoding="utf-8") as file:
                file.write("人工智能技术正在快速发展")
            with patch.object(sys, "argv", ["main.py", orig, copy, ans]):
                main()
            with open(ans, "r", encoding="utf-8") as file:
                self.assertEqual(file.read(), "1.00")

    def test_main_wrong_args(self):
        """参数数量错误时应触发 SystemExit"""
        with patch.object(sys, "argv", ["main.py"]):
            with self.assertRaises(SystemExit):
                main()

    def test_main_file_not_found(self):
        """文件不存在时应触发 SystemExit"""
        with patch.object(
            sys, "argv", ["main.py", "no1.txt", "no2.txt", "ans.txt"]
        ):
            with self.assertRaises(SystemExit):
                main()


if __name__ == '__main__':
    unittest.main()
