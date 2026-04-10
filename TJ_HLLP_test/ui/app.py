# -*- coding: utf-8 -*-
"""主应用界面"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import os

from config.manager import ConfigManager
from core.logic import DuiPaiLogic
from ui.widgets import ScrollableFrame, FileSelectRow
from ui.github_panel import GitHubPanel
from ui.styles import apply_styles

class DuiPaiApp:
    """对拍工具主应用"""
    
    def __init__(self, root):
        self.root = root
        self._setup_root()
        
        # 初始化模块
        self.config = ConfigManager()
        self.logic = DuiPaiLogic()
        self.msg_queue = queue.Queue()
        self.running = False
        self.gen_files_generated = set()
        
        # 绑定变量
        self._init_vars()
        
        # 构建界面
        self._create_ui()
        
        # 启动日志监听
        self._start_log_listener()
        
        # 注册关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_root(self):
        """窗口基础配置"""
        self.root.title("TJ_HLLP_test")
        self.root.geometry("1200x1000")
        apply_styles(self.root)
        
        # 高 DPI 支持
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    def _init_vars(self):
        """初始化 Tk 变量"""
        # 基础变量
        self.prefix_var = tk.StringVar(value=self.config.get("prefix"))
        self.test_dir_var = tk.StringVar(value=self.config.get("test_dir"))
        self.demo_dir_var = tk.StringVar(value=self.config.get("demo_dir"))
        self.gen_dir_var = tk.StringVar(value=self.config.get("gen_dir"))
        
        self.test_file_var = tk.StringVar(value=self.config.get("test_file"))
        self.demo_file_var = tk.StringVar(value=self.config.get("demo_file"))
        self.gen_file_var = tk.StringVar(value=self.config.get("gen_file"))
        
        self.use_gen_var = tk.BooleanVar(value=self.config.get("use_gen"))
        self.auto_clean_var = tk.BooleanVar(value=self.config.get("auto_clean"))
        
        self.compare_args_var = tk.StringVar(value=self.config.get("compare_args"))
        self.times_var = tk.StringVar(value=self.config.get("times"))
        self.time_limit_var = tk.StringVar(value=self.config.get("time_limit"))
        
        # 子文件夹变量（仅 Test）
        self.test_use_subfolder = tk.BooleanVar(value=self.config.get("test_use_subfolder", False))
        self.test_subfolder_var = tk.StringVar(value=self.config.get("test_subfolder", ""))
    
    def _create_ui(self):
        """构建主界面"""
        # 主滚动容器
        self.main_scroll = ScrollableFrame(self.root)
        self.main_scroll.pack(fill="both", expand=True)
        self.root.bind("<MouseWheel>", self._on_global_mousewheel)
        
        frame = self.main_scroll.scrollable_frame
        
        # 1. 文件配置
        self._create_config_section(frame)
        
        # 2. 路径选择
        self._create_path_section(frame)
        
        # 3. 对拍参数
        self._create_params_section(frame)
        
        # 4. GitHub 面板
        self.github_panel = GitHubPanel(frame, log_callback=self.log)
        self.github_panel.pack(fill="x", padx=15, pady=10)
        self.github_panel.load_config(self.config.config)
        
        # 5. 按钮区
        self._create_button_bar(frame)
        
        # 6. 日志区
        self._create_log_area(frame)
    
    def _create_config_section(self, parent):
        """创建文件配置区域"""
        frame = ttk.LabelFrame(
            parent, 
            text=" 1. 文件配置 (输入前缀后按回车自动填充) ", 
            padding=15
        )
        frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(frame, text="文件前缀:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.prefix_entry = ttk.Entry(frame, textvariable=self.prefix_var, width=25)
        self.prefix_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.prefix_entry.bind('<Return>', self.auto_fill_filenames)
        
        ttk.Checkbutton(
            frame, text="使用数据生成器 (Gen)", variable=self.use_gen_var,
            command=self.toggle_gen_input
        ).grid(row=0, column=2, padx=15)
        
        ttk.Checkbutton(
            frame, text="对拍成功后自动清理临时文件", variable=self.auto_clean_var
        ).grid(row=0, column=3, padx=10)
    
    def _create_path_section(self, parent):
        """创建路径选择区域"""
        frame = ttk.LabelFrame(
            parent, 
            text=" 2. 文件夹路径 & 文件名 ", 
            padding=15
        )
        frame.pack(fill="x", padx=15, pady=10)
        
        # Test 行（带子文件夹选项）
        FileSelectRow(
            frame, "待测程序 (Test):",
            self.test_dir_var, self.test_file_var,
            self.test_use_subfolder, self.test_subfolder_var
        ).pack(fill="x", pady=5)
        
        # Demo 行（简单）
        FileSelectRow(
            frame, "标准程序 (Demo):",
            self.demo_dir_var, self.demo_file_var
        ).pack(fill="x", pady=5)
        
        # Gen 行（简单）
        self.gen_row = FileSelectRow(
            frame, "数据生成 (Gen):",
            self.gen_dir_var, self.gen_file_var
        )
        self.gen_row.pack(fill="x", pady=5)
    
    def _create_params_section(self, parent):
        """创建对拍参数区域"""
        frame = ttk.LabelFrame(parent, text=" 3. 对拍参数 ", padding=15)
        frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(frame, text="txt_compare 参数:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.compare_args_var, width=50).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(frame, text="(例: --max_line 541 --trim all)", foreground="gray").grid(
            row=0, column=2, sticky="w", padx=5
        )
        
        frame_sub = ttk.Frame(frame)
        frame_sub.grid(row=1, column=0, columnspan=4, sticky="w", pady=10)
        
        ttk.Label(frame_sub, text="对拍次数:").pack(side="left", padx=5)
        ttk.Entry(frame_sub, textvariable=self.times_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(frame_sub, text="单点时限(秒):").pack(side="left", padx=20)
        ttk.Entry(frame_sub, textvariable=self.time_limit_var, width=10).pack(side="left", padx=5)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_button_bar(self, parent):
        """创建按钮栏"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=15, pady=10)
        
        self.btn_start = ttk.Button(frame, text="开始对拍", command=self.start_duipai)
        self.btn_start.pack(side="left", padx=20)
        
        self.btn_stop = ttk.Button(frame, text="停止", command=self.stop_duipai, state="disabled")
        self.btn_stop.pack(side="left", padx=20)
        
        ttk.Button(
            frame, text="清空日志", 
            command=lambda: self.log_text.delete('1.0', 'end')
        ).pack(side="right", padx=20)
        
        ttk.Button(frame, text="保存配置", command=self.save_current_config).pack(side="right", padx=10)
    
    def _create_log_area(self, parent):
        """创建日志区域"""
        frame = ttk.LabelFrame(parent, text=" 运行日志 ", padding=10)
        frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            frame, height=18, state='disabled',
            font=("Consolas", 16), wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True)
        
        # 设置颜色标签
        self.log_text.tag_config("INFO", foreground="#000000")
        self.log_text.tag_config("SUCCESS", foreground="#008000")
        self.log_text.tag_config("ERROR", foreground="#DC143C")
        self.log_text.tag_config("WARNING", foreground="#FF8C00")
        self.log_text.tag_config("CMD", foreground="#0000CD")
        self.log_text.tag_config("PATH", foreground="#4169E1")
        
        # ✅ 关键修复：将事件绑定到 Frame (容器) 和 Text 上
        # 这样鼠标在滚动条上时，Frame 也能拦截到事件
        frame.bind("<MouseWheel>", self._on_log_mousewheel)
        self.log_text.bind("<MouseWheel>", self._on_log_mousewheel)
    
    def _on_log_mousewheel(self, event):
        """日志滚轮：带防抖，到头后放行给主窗口"""
        # 防抖：间隔 < 16ms 的连续事件直接忽略（约 60Hz 屏幕刷新率）
        import time
        now = time.time()
        if hasattr(self, '_log_scroll_last') and now - self._log_scroll_last < 0.016:
            return "break"
        self._log_scroll_last = now

        delta = int(-1 * (event.delta / 120))
        view = self.log_text.yview()
        if (delta < 0 and view[0] > 0.0) or (delta > 0 and view[1] < 1.0):
            self.log_text.yview_scroll(delta, "units")
            return "break"
        # 到头/底：不拦截，事件自然冒泡给主窗口

    def _on_global_mousewheel(self, event):
        """主窗口滚轮：同样添加防抖"""
        import time
        now = time.time()
        if hasattr(self, '_main_scroll_last') and now - self._main_scroll_last < 0.016:
            return
        self._main_scroll_last = now

        focus = self.root.focus_get()
        if focus and isinstance(focus, (ttk.Entry, tk.Entry)):
            return
        self.main_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _start_log_listener(self):
        """安全日志监听（主线程轮询，不占 CPU）"""
        def check():
            try:
                while True:
                    msg, tag = self.msg_queue.get_nowait()
                    self.log_text.config(state='normal')
                    self.log_text.insert('end', msg + "\n", tag)
                    self.log_text.see('end')
                    self.log_text.config(state='disabled')
            except queue.Empty:
                pass
            # 50ms 检查一次，CPU 占用 < 0.1%
            self.root.after(50, check)
        check()
    
    def log(self, message, tag="INFO"):
        """添加日志"""
        self.msg_queue.put((message, tag))
    
    def auto_fill_filenames(self, event=None):
        """自动填充文件名"""
        prefix = self.prefix_var.get().strip()
        if not prefix:
            return
        
        self.test_file_var.set(f"{prefix}.exe")
        self.demo_file_var.set(f"{prefix}-demo.exe")
        self.gen_file_var.set(f"{prefix}-gen.exe")
        self.test_subfolder_var.set(prefix)
        
        self.log(f"已根据前缀 '{prefix}' 自动填充文件名和子文件夹名", "SUCCESS")
    
    def toggle_gen_input(self):
        """切换 Gen 行显示"""
        if self.use_gen_var.get():
            self.gen_row.pack(fill="x", pady=5)
        else:
            self.gen_row.pack_forget()
    
    def _build_path(self, dir_var, file_var, use_sub_var=None, sub_var=None):
        """构建完整文件路径"""
        if not dir_var.get() or not file_var.get():
            return None
        path = dir_var.get()
        if use_sub_var and use_sub_var.get() and sub_var and sub_var.get().strip():
            path = os.path.join(path, sub_var.get().strip())
        return os.path.join(path, file_var.get())
    
    def start_duipai(self):
        """开始对拍"""
        if self.running:
            return
        
        # 获取路径
        test_file = self._build_path(
            self.test_dir_var, self.test_file_var,
            self.test_use_subfolder, self.test_subfolder_var
        )
        demo_file = self._build_path(self.demo_dir_var, self.demo_file_var)
        gen_file = None
        
        if self.use_gen_var.get():
            gen_file = self._build_path(self.gen_dir_var, self.gen_file_var)
        
        # 检查文件
        errors = []
        if not test_file or not os.path.exists(test_file):
            errors.append(f"未找到测试程序: {test_file}")
        if not demo_file or not os.path.exists(demo_file):
            errors.append(f"未找到标准程序: {demo_file}")
        if self.use_gen_var.get() and (not gen_file or not os.path.exists(gen_file)):
            errors.append(f"未找到数据生成器: {gen_file}")
        
        if errors:
            messagebox.showerror("文件缺失", "\n".join(errors))
            return
        
        # 启动
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.log_text.delete('1.0', 'end')
        
        self.log("=" * 60, "CMD")
        self.log("           TJ_HLLP_test", "CMD")
        self.log("=" * 60, "CMD")
        self.log(f"测试程序: {test_file}", "PATH")
        self.log(f"标准程序: {demo_file}", "PATH")
        if gen_file:
            self.log(f"数据生成: {gen_file}", "PATH")
        self.log(f"参数: {self.compare_args_var.get()}")
        self.log(f"次数: {self.times_var.get()} | 时限: {self.time_limit_var.get()}秒")
        if self.auto_clean_var.get():
            self.log("模式: 开启自动清理", "WARNING")
        self.log("=" * 60, "CMD")
        
        # 后台线程
        t = threading.Thread(
            target=self.run_loop, 
            args=(test_file, demo_file, gen_file),
            daemon=True
        )
        t.start()
    
    def stop_duipai(self):
        """停止对拍"""
        self.running = False
        self.log("⚠ 用户停止对拍...", "WARNING")
    
    def run_loop(self, test_exe, demo_exe, gen_exe):
        """对拍主循环"""
        times = int(self.times_var.get())
        time_limit = float(self.time_limit_var.get())
        compare_args = self.compare_args_var.get()
        
        temp_in = "duipai_in.txt"
        temp_std_out = "duipai_out_std.txt"
        temp_test_out = "duipai_out_test.txt"
        
        global_success = True
        
        for i in range(1, times + 1):
            if not self.running:
                break
            
            self.log(f"\n第 {i} 组...", "INFO")
            
            # 生成数据
            if gen_exe:
                gen_dir = os.path.dirname(gen_exe)
                
                if self.auto_clean_var.get():
                    try:
                        all_files_before = set(os.listdir(gen_dir))
                    except:
                        self.auto_clean_var.set(False)
                        self.log("⚠ 无法读取生成器目录，自动清理已禁用", "WARNING")
                        all_files_before = set()
                else:
                    all_files_before = set()
                
                cmd_gen = self.logic.get_run_command(gen_exe)
                status, err = self.logic.run_program(cmd_gen, None, temp_in, time_limit)
                
                if status != "AC":
                    self.log(f"  [Gen] {status}: {err}", "ERROR")
                    global_success = False
                    break
                
                # 记录生成的文件
                if self.auto_clean_var.get() and all_files_before:
                    try:
                        all_files_after = set(os.listdir(gen_dir))
                        generated = all_files_after - all_files_before
                        generated = {f for f in generated if not f.startswith('~$')}
                        self.gen_files_generated = generated
                        if generated:
                            self.log(f"  [Clean] 检测到 {len(generated)} 个新文件", "INFO")
                    except:
                        pass
            
            # 运行 Demo
            cmd_demo = self.logic.get_run_command(demo_exe)
            status_std, err_std = self.logic.run_program(
                cmd_demo, temp_in, temp_std_out, time_limit
            )
            if status_std != "AC":
                self.log(f"  [Demo] {status_std}: {err_std}", "ERROR")
                global_success = False
                break
            
            # 运行 Test
            cmd_test = self.logic.get_run_command(test_exe)
            status_test, err_test = self.logic.run_program(
                cmd_test, temp_in, temp_test_out, time_limit
            )
            if status_test != "AC":
                self.log(f"  [Test] {status_test}: {err_test}", "ERROR")
                global_success = False
                break
            
            # 比对
            is_same, diff = self.logic.compare_files(
                temp_std_out, temp_test_out, compare_args
            )
            
            if not is_same:
                self.log(f"  [WA] 发现不同!", "ERROR")
                self.log(f"  差异:\n{diff}", "ERROR")
                self.log(">>> 保留现场文件", "WARNING")
                global_success = False
                break
            else:
                if i % 10 == 0 or i == times:
                    self.log(f"  [OK] 已通过 {i} 组", "SUCCESS")
        
        # 结束
        if self.running:
            if global_success:
                self.log("\n" + "=" * 60, "SUCCESS")
                self.log("           ✓ 对拍全部通过!", "SUCCESS")
                self.log("=" * 60, "SUCCESS")
                self.clean_generated_files()
            else:
                self.log("\n" + "=" * 60, "ERROR")
                self.log("           ✗ 对拍失败", "ERROR")
                self.log("=" * 60, "ERROR")
        else:
            self.log("\n⚠ 对拍已中断", "WARNING")
        
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
    
    def clean_generated_files(self):
        """清理生成的临时文件"""
        if not self.auto_clean_var.get() or not self.gen_files_generated:
            return
        
        gen_dir = self.gen_dir_var.get()
        if not gen_dir:
            return
        
        self.log(f"\n正在清理 {len(self.gen_files_generated)} 个临时文件...", "INFO")
        count = 0
        for filename in self.gen_files_generated:
            try:
                filepath = os.path.join(gen_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    count += 1
            except Exception as e:
                self.log(f"  删除失败 {filename}: {e}", "WARNING")
        
        self.log(f"✓ 清理完成，删除 {count} 个文件", "SUCCESS")
        self.gen_files_generated.clear()
    
    def save_current_config(self):
        """手动保存配置"""
        data = {
            "prefix": self.prefix_var.get(),
            "test_dir": self.test_dir_var.get(),
            "demo_dir": self.demo_dir_var.get(),
            "gen_dir": self.gen_dir_var.get(),
            "test_file": self.test_file_var.get(),
            "demo_file": self.demo_file_var.get(),
            "gen_file": self.gen_file_var.get(),
            "use_gen": self.use_gen_var.get(),
            "auto_clean": self.auto_clean_var.get(),
            "compare_args": self.compare_args_var.get(),
            "times": self.times_var.get(),
            "time_limit": self.time_limit_var.get(),
            "test_use_subfolder": self.test_use_subfolder.get(),
            "test_subfolder": self.test_subfolder_var.get(),
        }
        data.update(self.github_panel.get_config())
        
        if self.config.save_config(data):
            messagebox.showinfo("成功", "配置已保存！")
            self.log("✓ 配置已保存到 duipai_config.json", "SUCCESS")
        else:
            messagebox.showerror("错误", "保存配置失败")
    
    def on_closing(self):
        """窗口关闭时保存配置"""
        data = {
            "prefix": self.prefix_var.get(),
            "test_dir": self.test_dir_var.get(),
            "demo_dir": self.demo_dir_var.get(),
            "gen_dir": self.gen_dir_var.get(),
            "test_file": self.test_file_var.get(),
            "demo_file": self.demo_file_var.get(),
            "gen_file": self.gen_file_var.get(),
            "use_gen": self.use_gen_var.get(),
            "auto_clean": self.auto_clean_var.get(),
            "compare_args": self.compare_args_var.get(),
            "times": self.times_var.get(),
            "time_limit": self.time_limit_var.get(),
            "test_use_subfolder": self.test_use_subfolder.get(),
            "test_subfolder": self.test_subfolder_var.get(),
        }
        data.update(self.github_panel.get_config())
        self.config.save_config(data)
        self.root.destroy()