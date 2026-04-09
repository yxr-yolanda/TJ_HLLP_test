# -*- coding: utf-8 -*-
"""自定义 UI 组件"""
import tkinter as tk
from tkinter import ttk, filedialog

class ScrollableFrame(ttk.Frame):
    """可滚动 Frame 组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window, width=event.width)
    
    def yview_scroll(self, *args):
        self.canvas.yview_scroll(*args)
    
    def yview_moveto(self, pos):
        self.canvas.yview_moveto(pos)


class FileSelectRow(ttk.Frame):
    """文件选择行组件（支持子文件夹选项）"""
    
    def __init__(self, parent, label, dir_var, file_var, 
                 use_subfolder_var=None, subfolder_var=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.use_subfolder_var = use_subfolder_var
        self.subfolder_var = subfolder_var
        
        # 第一行：目录 + 浏览按钮 + 文件名
        ttk.Label(self, text=label, width=16).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        
        ttk.Entry(self, textvariable=dir_var, width=35).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(self, text="浏览...", width=8, 
                  command=lambda: self._browse(dir_var)).grid(row=0, column=2, padx=5)
        
        ttk.Label(self, text="文件名:").grid(row=0, column=3, sticky="e", padx=10)
        ttk.Entry(self, textvariable=file_var, width=20).grid(row=0, column=4, sticky="w")
        
        # 第二行：子文件夹选项（可选）
        if use_subfolder_var and subfolder_var:
            self.subfolder_cb = ttk.Checkbutton(
                self, text="使用子文件夹:", variable=use_subfolder_var
            )
            self.subfolder_cb.grid(row=1, column=0, sticky="e", padx=5, pady=2)
            
            self.subfolder_entry = ttk.Entry(self, textvariable=subfolder_var, width=15)
            self.subfolder_entry.grid(row=1, column=1, sticky="w", padx=5)
            
            # 初始状态
            if not use_subfolder_var.get():
                self.subfolder_entry.grid_remove()
            
            use_subfolder_var.trace_add('write', self._toggle_subfolder)
        
        self.columnconfigure(1, weight=1)
    
    def _browse(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
    
    def _toggle_subfolder(self, *args):
        if self.use_subfolder_var.get():
            self.subfolder_entry.grid()
        else:
            self.subfolder_entry.grid_remove()