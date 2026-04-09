# -*- coding: utf-8 -*-
"""UI 样式配置"""

def apply_styles(root, font_size=17, font_family="SimSun"):
    """应用全局字体样式"""
    root.option_add("*Font", f"{font_family} {font_size}")
    root.option_add("*Entry.Font", f"{font_family} {font_size}")
    root.option_add("*Text.Font", f"{font_family} {font_size}")
    
    style = ttk.Style()
    style.configure('.', font=(font_family, font_size))
    style.configure('TLabel', font=(font_family, font_size))
    style.configure('TButton', font=(font_family, font_size))
    style.configure('TEntry', font=(font_family, font_size))
    style.configure('TCheckbutton', font=(font_family, font_size))
    style.configure('TLabelframe', font=(font_family, font_size))
    style.configure('TLabelframe.Label', font=(font_family, font_size, 'bold'))
    style.configure('TNotebook.Tab', font=(font_family, font_size + 2))

# 需要导入 ttk
import tkinter as tk
from tkinter import ttk