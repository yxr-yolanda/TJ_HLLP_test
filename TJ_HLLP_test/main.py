# -*- coding: utf-8 -*-
"""
本地对拍工具 - 主入口
作者：TJ_HLLP_test
版本：2.0
"""
import sys
import tkinter as tk
from ui.app import DuiPaiApp

def main():
    """程序入口"""
    root = tk.Tk()
    app = DuiPaiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()