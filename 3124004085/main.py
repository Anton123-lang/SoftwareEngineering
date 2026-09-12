"""
论文查重程序
基于 jieba 分词 + 余弦相似度计算两篇论文的重复率
用法: python main.py <原文路径> <抄袭版路径> <答案输出路径>
"""
import sys
import re
import math
from collections import Counter

import jieba


class FileEncodingError(Exception):
    """自定义异常：文件编码错误"""


def read_file(file_path):
    """
    读取 UTF-8 文本文件。

    :param file_path: 文件绝对或相对路径
    :return: 文件文本内容
    :raises FileNotFoundError: 文件不存在
    :raises FileEncodingError: 文件不是 UTF-8 编码
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"文件不存在: {file_path}") from exc
    except UnicodeDecodeError as exc:
        raise FileEncodingError(f"文件编码错误，请使用UTF-8: {file_path}") from exc


def segment(text):
    """
    对文本进行分词，去除标点符号与单字。

    :param text: 原始文本
    :return: 词语列表
    """
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    words = jieba.lcut(text)
    return [word for word in words if len(word) > 1]


def build_word_freq(words):
    """
    统计词频。

    :param words: 词语列表
    :return: Counter 词频对象
    """
    return Counter(words)


def cosine_similarity(freq1, freq2):
    """
    计算两个词频向量的余弦相似度。

    :param freq1: 词频字典 1
    :param freq2: 词频字典 2
    :return: 相似度，范围 [0, 1]
    """
    all_words = set(freq1.keys()) | set(freq2.keys())
    vec1 = [freq1.get(word, 0) for word in all_words]
    vec2 = [freq2.get(word, 0) for word in all_words]
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def compute_similarity(orig_text, copy_text):
    """
    综合计算两篇文本的重复率。

    :param orig_text: 原文
    :param copy_text: 抄袭版
    :return: 相似度浮点数
    """
    if not orig_text.strip() or not copy_text.strip():
        return 0.0
    freq1 = build_word_freq(segment(orig_text))
    freq2 = build_word_freq(segment(copy_text))
    return cosine_similarity(freq1, freq2)


def parse_arguments(args):
    """
    解析命令行参数。

    :param args: sys.argv 列表
    :return: (原文路径, 抄袭路径, 答案路径)
    :raises ValueError: 参数数量不为 4
    """
    if len(args) != 4:
        raise ValueError("用法: python main.py <原文路径> <抄袭路径> <答案路径>")
    return args[1], args[2], args[3]


def write_result(ans_path, similarity):
    """
    将相似度结果写入答案文件（保留两位小数）。

    :param ans_path: 答案文件路径
    :param similarity: 相似度浮点数
    """
    with open(ans_path, 'w', encoding='utf-8') as file:
        file.write(f"{similarity:.2f}")


def main():
    """程序入口。"""
    try:
        orig_path, copy_path, ans_path = parse_arguments(sys.argv)
    except ValueError as err:
        print(err)
        sys.exit(1)

    try:
        orig_text = read_file(orig_path)
        copy_text = read_file(copy_path)
    except (FileNotFoundError, FileEncodingError) as err:
        print(f"读取文件失败: {err}")
        sys.exit(1)

    similarity = compute_similarity(orig_text, copy_text)

    try:
        write_result(ans_path, similarity)
    except OSError as err:
        print(f"写入答案文件失败: {err}")
        sys.exit(1)


if __name__ == '__main__':
    main()
