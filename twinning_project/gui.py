"""tkinter 图形界面（等价于命令行的生成功能）。"""

import tkinter as tk
from tkinter import messagebox, scrolledtext

from generator import generate_exercises
from utils import fraction_to_string, save_lines


class App:
    def __init__(self, root):
        self.root = root
        root.title('小学四则运算题目生成器')
        root.geometry('760x540')

        top = tk.Frame(root)
        top.pack(pady=8)

        tk.Label(top, text='题目数量:').pack(side=tk.LEFT)
        self.n_var = tk.StringVar(value='10')
        tk.Entry(top, textvariable=self.n_var, width=8).pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(top, text='数值范围 r:').pack(side=tk.LEFT)
        self.r_var = tk.StringVar(value='10')
        tk.Entry(top, textvariable=self.r_var, width=8).pack(side=tk.LEFT, padx=(0, 12))

        tk.Button(top, text='生成题目', command=self.generate).pack(side=tk.LEFT)
        tk.Button(top, text='保存到文件', command=self.save).pack(side=tk.LEFT, padx=6)

        self.text = scrolledtext.ScrolledText(root, font=('Consolas', 11))
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.exercises = []

    def generate(self):
        try:
            n = int(self.n_var.get())
            r = int(self.r_var.get())
        except ValueError:
            messagebox.showerror('参数错误', '题目数量和数值范围必须是整数')
            return
        if n <= 0 or r < 2:
            messagebox.showerror('参数错误', '题目数量需大于 0，数值范围需不小于 2')
            return
        try:
            self.exercises = generate_exercises(n, r)
        except Exception as e:
            messagebox.showerror('生成失败', str(e))
            return

        self.text.delete('1.0', tk.END)
        for i, ex in enumerate(self.exercises, 1):
            self.text.insert(
                tk.END,
                f"{i:>4}. {ex.text():<28}\t{fraction_to_string(ex.answer)}\n",
            )

    def save(self):
        if not self.exercises:
            messagebox.showwarning('提示', '请先生成题目')
            return
        save_lines('Exercises.txt', [ex.text() for ex in self.exercises])
        save_lines('Answers.txt', [fraction_to_string(ex.answer) for ex in self.exercises])
        messagebox.showinfo('保存成功', '已写入 Exercises.txt 和 Answers.txt')


def launch():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    launch()