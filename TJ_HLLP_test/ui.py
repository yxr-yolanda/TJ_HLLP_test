import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Canvas
import threading
import queue
import os
import json
import urllib.request
import urllib.parse
import html

from config import ConfigManager
from logic import DuiPaiLogic

class DuiPaiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TJ_HLLP_test")
        self.root.geometry("1200x1000")

        #========== 字体配置开始 ==========
        FONT_SIZE = 17  # 在这里调整字体大小
        font_type="SimSun" # 在这里调整字体

        self.root.option_add("*Font", f"{font_type} {FONT_SIZE}")
        self.root.option_add("*Entry.Font", f"{font_type} {FONT_SIZE}")
        self.root.option_add("*Text.Font", f"{font_type} {FONT_SIZE}")
        
        style = ttk.Style()
        style.configure('.', font=(f'{font_type}', FONT_SIZE))
        style.configure('TLabel', font=(f'{font_type}', FONT_SIZE))
        style.configure('TButton', font=(f'{font_type}', FONT_SIZE))
        style.configure('TEntry', font=(f'{font_type}', FONT_SIZE))
        style.configure('TCheckbutton', font=(f'{font_type}', FONT_SIZE))
        style.configure('TLabelframe', font=(f'{font_type}', FONT_SIZE))
        style.configure('TLabelframe.Label', font=(f'{font_type}', FONT_SIZE, 'bold'))
        style.configure('TNotebook.Tab', font=(f'{font_type}', FONT_SIZE + 2))
        
        style.configure('Title.TLabelframe.Label', font=(f'{font_type}', FONT_SIZE + 2, 'bold'))
        # ========== 字体配置结束 ==========

        # 设置高DPI支持
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # 初始化配置管理器
        self.config = ConfigManager()
        self.logic = DuiPaiLogic()
        self.running = False
        self.msg_queue = queue.Queue()
        
        # 变量 - 从配置加载
        self.prefix_var = tk.StringVar(value=self.config.get("prefix", ""))
        self.test_dir_var = tk.StringVar(value=self.config.get("test_dir", ""))
        self.demo_dir_var = tk.StringVar(value=self.config.get("demo_dir", ""))
        self.gen_dir_var = tk.StringVar(value=self.config.get("gen_dir", ""))
        
        self.test_file_var = tk.StringVar(value=self.config.get("test_file", ".exe"))
        self.demo_file_var = tk.StringVar(value=self.config.get("demo_file", "-demo.exe"))
        self.gen_file_var = tk.StringVar(value=self.config.get("gen_file", "-gen.exe"))
        
        self.use_gen_var = tk.BooleanVar(value=self.config.get("use_gen", True))
        self.auto_clean_var = tk.BooleanVar(value=self.config.get("auto_clean", False))
        
        self.compare_args_var = tk.StringVar(value=self.config.get("compare_args", "--max_line 0"))
        self.times_var = tk.StringVar(value=self.config.get("times", "100"))
        self.time_limit_var = tk.StringVar(value=self.config.get("time_limit", "1.0"))
        
        # GitHub 相关变量
        self.gh_token_var = tk.StringVar(value=self.config.get("gh_token", ""))
        self.gh_url_var = tk.StringVar(value=self.config.get("gh_url", "https://github.com/"))
        self.gh_branch_var = tk.StringVar(value=self.config.get("gh_branch", "main"))
        self.gh_save_dir_var = tk.StringVar(value=self.config.get("gh_save_dir", ""))
        self.gh_proxy_var = tk.StringVar(value=self.config.get("gh_proxy", ""))

        self.gen_files_generated = set()
        
        # ================= 新增：主窗口滚动容器 =================
        self.main_canvas = tk.Canvas(root)
        self.main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollable_frame = ttk.Frame(self.main_canvas)

        self.main_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # ================= 主窗口滚动容器（无固定滚动条）=================
        self.main_canvas = tk.Canvas(root, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollable_frame = ttk.Frame(self.main_canvas)

        self.main_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # 让内部 frame 宽度跟随 canvas
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)

        self.main_canvas.create_window((0, 0), window=self.main_scrollable_frame, anchor="nw", width=0)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # 布局：canvas 在左，滚动条在右
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # 绑定全局滚轮
        self.root.bind("<MouseWheel>", self._on_mousewheel)
        # ========================================================

        self.create_widgets()
        self.check_queue()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _on_canvas_configure(self, event):
        """让内部 frame 宽度跟随 canvas 变化"""
        self.main_canvas.itemconfig(self.main_canvas.find_withtag("all")[0], width=event.width)

    def _on_main_mousewheel(self, event):
        """主窗口滚动处理"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_gh_frame_configure(self, event):
        """当内部 frame 内容变化时，自动更新 scrollregion"""
        # 设置 scrollregion 为内部 frame 的实际边界
        self.gh_canvas.configure(scrollregion=self.gh_canvas.bbox("all"))
        
    def _on_gh_canvas_configure(self, event):
        """当 Canvas 宽度变化时，同步调整内部 frame 的宽度"""
        self.gh_canvas.itemconfig(self.gh_canvas_window, width=event.width)

    def create_github_frame(self, parent):
        frame_gh = ttk.LabelFrame(parent, text=" 4. 从 GitHub 下载数据生成器 ", padding=15)
        frame_gh.pack(fill="x", padx=15, pady=10)

        # === 配置网格权重，让第 1 列（输入框列）自动伸缩 ===
        frame_gh.columnconfigure(1, weight=1)
        frame_gh.columnconfigure(3, weight=1) # 如果有需要
        # frame_gh.rowconfigure(3, weight=1)    # 让文件列表区域高度可伸缩

        # --- 第一行：Token 和 分支 ---
        ttk.Label(frame_gh, text="GitHub Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame_gh, textvariable=self.gh_token_var, show="*").grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(frame_gh, text="分支:").grid(row=0, column=2, sticky="e", padx=(15, 5), pady=5)
        ttk.Entry(frame_gh, textvariable=self.gh_branch_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # --- 第二行：代理地址 ---
        ttk.Label(frame_gh, text="代理地址:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame_gh, textvariable=self.gh_proxy_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(frame_gh, text="(例: http://127.0.0.1:7890)", foreground="gray").grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        # --- 第三行：仓库链接 & 获取按钮 ---
        ttk.Label(frame_gh, text="仓库链接:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame_gh, textvariable=self.gh_url_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame_gh, text="获取文件列表", command=self.fetch_github_files_thread).grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

# --- 第四行：文件列表区域 ---
        ttk.Label(frame_gh, text="仓库文件:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        
        # 这是一个容器 Frame，鼠标在它的灰色背景上时也需要响应滚轮
        self.gh_list_container = ttk.Frame(frame_gh, relief="sunken", borderwidth=1)
        self.gh_list_container.grid(row=3, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # 内部 Canvas
        self.gh_canvas = Canvas(self.gh_list_container, bg="white", highlightthickness=0)
        self.gh_scrollbar = ttk.Scrollbar(self.gh_list_container, orient="vertical", command=self.gh_canvas.yview)
        self.gh_scrollable_frame = ttk.Frame(self.gh_canvas)

        # 创建窗口，锚点设为左上角 (nw)
        self.gh_canvas_window = self.gh_canvas.create_window((0, 0), window=self.gh_scrollable_frame, anchor="nw")
        self.gh_canvas.configure(yscrollcommand=self.gh_scrollbar.set)

        self.gh_canvas.pack(side="left", fill="both", expand=True)
        self.gh_scrollbar.pack(side="right", fill="y")
        
        # 绑定配置事件
        self.gh_scrollable_frame.bind("<Configure>", self._on_gh_frame_configure)
        self.gh_canvas.bind("<Configure>", self._on_gh_canvas_configure)
        
        # 【关键修改】：将滚轮同时绑定到 容器(灰色) 和 Canvas(白色)
        self.gh_list_container.bind("<MouseWheel>", self._on_gh_mousewheel)
        self.gh_canvas.bind("<MouseWheel>", self._on_gh_mousewheel) 

        self.gh_check_vars = [] 
        self.gh_file_data_map = {} 

        # --- 第五行：保存路径 ---
        ttk.Label(frame_gh, text="保存到目录:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame_gh, textvariable=self.gh_save_dir_var).grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frame_gh, text="浏览...", command=lambda: self.browse_folder(self.gh_save_dir_var)).grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- 第六行：下载按钮 ---
        self.btn_gh_download = ttk.Button(frame_gh, text="下载选中文件 (0)", command=self.download_gh_files_thread, state="disabled")
        self.btn_gh_download.grid(row=5, column=1, columnspan=3, padx=5, pady=10, sticky="ew")

    def _on_mousewheel(self, event):
        """全局滚轮处理 - 排除输入框"""
        # 获取当前焦点控件
        focus_widget = self.root.focus_get()
        
        # 如果焦点在 Entry, Text, ScrolledText 等输入控件上，不触发全局滚动
        if focus_widget and isinstance(focus_widget, (ttk.Entry, tk.Entry, tk.Text, scrolledtext.ScrolledText)):
            return
            
        # 否则滚动主 canvas
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_gh_mousewheel(self, event):
        """
        智能滚轮处理：
        1. 如果鼠标在列表区域，优先滚动列表。
        2. 如果列表已经滚到顶（或底），则允许事件冒泡，滚动主窗口。
        """
        # Windows 下 delta 为 120 (向上) 或 -120 (向下)
        delta = int(-1 * (event.delta / 120))

        # 获取当前滚动位置 (0.0 是顶，1.0 是底)
        view = self.gh_canvas.yview()
        top_pos = view[0]
        bottom_pos = view[1]

        can_scroll_list = False
        
        # 判断是否可以继续滚动列表
        if delta < 0: # 向上滚
            if top_pos > 0.0: # 还没到顶
                can_scroll_list = True
        elif delta > 0: # 向下滚
            if bottom_pos < 1.0: # 还没到底
                can_scroll_list = True
        
        if can_scroll_list:
            # 执行列表滚动
            self.gh_canvas.yview_scroll(delta, "units")
            return "break" # 拦截事件，不再传给主窗口
        else:
            # 到达边缘，返回空值（不 return "break"），让事件冒泡到父窗口
            return

    def _get_github_opener(self):
        """构建支持代理和 Token 的 Opener"""
        handlers = []
        
        # 1. 处理代理
        proxy_url = self.gh_proxy_var.get().strip()
        if proxy_url:
            # 支持 http, https
            proxies = {'http': proxy_url, 'https': proxy_url}
            proxy_handler = urllib.request.ProxyHandler(proxies)
            handlers.append(proxy_handler)
            self.log(f"使用代理: {proxy_url}", "INFO")
        
        # 2. 处理 Token
        token = self.gh_token_var.get().strip()
        if token:
            # 创建一个自定义的处理器来添加 Header
            class TokenHandler(urllib.request.BaseHandler):
                def __init__(self, token_str):
                    self.token = token_str
                
                def http_request(self, request):
                    request.add_header("Authorization", f"token {self.token}")
                    request.add_header("User-Agent", "DuiPai-Tool")
                    return request
                
                https_request = http_request # HTTPS 同理

            handlers.append(TokenHandler(token))
        
        # 如果没有 Token，也要加 User-Agent
        if not token:
            class UAHandler(urllib.request.BaseHandler):
                def http_request(self, request):
                    request.add_header("User-Agent", "DuiPai-Tool")
                    return request
                https_request = http_request
            handlers.append(UAHandler())

        return urllib.request.build_opener(*handlers)

    def fetch_github_files_thread(self):
        """多线程获取文件列表"""
        self.btn_gh_download.config(state="disabled")
        
        # 清空旧数据
        for widget in self.gh_scrollable_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.gh_scrollable_frame, text="正在连接 GitHub API，请稍候...").pack(pady=20)
        
        t = threading.Thread(target=self._fetch_github_files_worker)
        t.daemon = True
        t.start()

    def _fetch_github_files_worker(self):
        """后台获取文件列表"""
        try:
            url = self.gh_url_var.get().strip()
            branch = self.gh_branch_var.get().strip() or "main"
            
            # 1. 自动补全协议
            if not url.startswith("http"):
                url = "https://" + url
            
            if "github.com" not in url:
                raise ValueError("请输入有效的 GitHub 链接")
            
            # 2. 解析 URL
            parsed = urllib.parse.urlparse(url)
            path_parts = [p for p in parsed.path.split("/") if p]
            
            # 处理 github.com 前缀
            if path_parts and path_parts[0] == "github.com":
                path_parts = path_parts[1:]
            
            if len(path_parts) < 2:
                raise ValueError(f"链接太短，无法解析: {path_parts}")
            
            owner = path_parts[0]
            repo = path_parts[1]
            
            # 确定子路径 (自动识别 /tree/main/folder 或直接 /folder)
            target_path = ""
            if len(path_parts) > 2:
                if path_parts[2] == 'tree' and len(path_parts) > 4:
                     target_path = "/".join(path_parts[4:])
                elif path_parts[2] != 'tree':
                     target_path = "/".join(path_parts[2:])
            
            # 构建 API URL
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{target_path}"
            if branch:
                api_url += f"?ref={branch}"
            
            self.root.after(0, lambda u=api_url: self.log(f"正在请求: {u}", "INFO"))

            # 3. 使用自定义 Opener 发起请求 (包含代理和 Token)
            opener = self._get_github_opener()
            
            try:
                with opener.open(api_url, timeout=15) as response:
                    raw_data = response.read()
                    try:
                        data = json.loads(raw_data.decode('utf-8'))
                    except json.JSONDecodeError:
                        raise Exception("API 返回数据格式错误（可能是私有仓库或链接无效）")
                    
                    self.root.after(0, self._update_file_list, data)
                    
            except urllib.error.HTTPError as e:
                # 捕获 404, 403 等错误
                err_msg = f"GitHub 返回错误代码: {e.code}\n"
                if e.code == 404:
                    err_msg += "找不到仓库或文件夹。请检查链接是否正确，或分支名是否为 'main'/'master'。"
                elif e.code == 403:
                    err_msg += "访问被拒绝。可能触发了 API 限制，请检查 Token 是否有效，或稍后再试。"
                raise Exception(err_msg)
                
            except urllib.error.URLError as e:
                raise Exception(f"网络连接失败: {e.reason}\n请检查代理设置或网络连接。")

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.log(f"GitHub获取失败: {msg}", "ERROR"))

    def _update_file_list(self, data):
        """更新文件列表 UI - 生成复选框"""
        # 清空旧数据
        for widget in self.gh_scrollable_frame.winfo_children():
            widget.destroy()
        self.gh_check_vars = []
        self.gh_file_data_map = {}
        
        file_count = 0
        
        for item in data:
            if item['type'] == 'file':
                if item['name'].endswith(('.py', '.cpp', '.c', '.exe', '.java')):
                    var = tk.BooleanVar(value=False)
                    self.gh_check_vars.append({'name': item['name'], 'var': var, 'data': item})
                    self.gh_file_data_map[item['name']] = item
                    
                    cb = ttk.Checkbutton(self.gh_scrollable_frame, 
                                         text=f"{item['name']} ({item['size']} bytes)", 
                                         variable=var,
                                         command=self._update_download_button_text)
                    # 使用 pack 填充
                    cb.pack(anchor="w", padx=10, pady=2, fill="x")
                    file_count += 1
        
        if file_count == 0:
            ttk.Label(self.gh_scrollable_frame, text="当前目录下未找到支持的生成器文件").pack(pady=20)
            
        self._update_download_button_text()
        
        # === 关键修复：强制刷新布局并消除顶部留白 ===
        self.root.update_idletasks() # 等待布局计算完成
        
        # 获取内部 frame 的实际大小
        w = self.gh_scrollable_frame.winfo_reqwidth()
        h = self.gh_scrollable_frame.winfo_reqheight()
        
        # 强制设置 scrollregion 从 (0,0) 开始，消除顶部偏移
        self.gh_canvas.config(scrollregion=(0, 0, w, h))
        
        # 强制滚动到顶部
        self.gh_canvas.yview_moveto(0.0)
    
    def _update_download_button_text(self):
        """更新下载按钮上的选中数量"""
        count = sum(1 for item in self.gh_check_vars if item['var'].get())
        text = f"下载选中文件 ({count})"
        self.btn_gh_download.config(text=text)
        if count > 0:
            self.btn_gh_download.config(state="normal")
        else:
            self.btn_gh_download.config(state="disabled")

    def on_gh_file_click(self, event):
        """处理文件列表点击事件"""
        index = self.gh_file_list.index(f"@{event.x},{event.y}")
        line = int(index.split('.')[0])
        
        # 获取当前点击行的文件名
        self.gh_file_list.config(state='normal')
        line_text = self.gh_file_list.get(f"{line}.0", f"{line}.end").strip()
        self.gh_file_list.config(state='disabled')
        
        if not line_text.startswith("📄"):
            return
            
        filename = line_text.split(" ")[1]
        # 从缓存数据中查找
        for item in self.gh_repo_data:
            if item['type'] == 'file' and item['name'] == filename:
                self.gh_selected_file = item
                self.btn_gh_download.config(state="normal")
                self.gh_file_list.tag_remove("sel", "1.0", "end")
                self.gh_file_list.tag_add("sel", f"{line}.0", f"{line}.end")
                self.log(f"已选中: {filename}", "INFO")
                break

    def download_gh_files_thread(self):
        """多线程批量下载文件"""
        # 获取选中的文件
        selected_items = [item for item in self.gh_check_vars if item['var'].get()]
        
        if not selected_items:
            messagebox.showwarning("提示", "请先勾选要下载的文件")
            return
            
        save_dir = self.gh_save_dir_var.get().strip()
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except:
                messagebox.showerror("错误", "无法创建保存目录")
                return
        
        # 锁定按钮，防止重复点击
        self.btn_gh_download.config(state="disabled")
        
        # 启动后台线程，传入选中的文件列表
        t = threading.Thread(target=self._download_gh_files_worker, args=(selected_items, save_dir))
        t.daemon = True
        t.start()

    def _download_gh_files_worker(self, selected_items, save_dir):
        """后台批量下载逻辑"""
        total = len(selected_items)
        success_count = 0
        fail_count = 0
        
        for idx, item_info in enumerate(selected_items, 1):
            filename = item_info['name']
            file_data = item_info['data']
            download_url = file_data['download_url']
            save_path = os.path.join(save_dir, filename)
            
            # 更新日志
            self.root.after(0, lambda f=filename, i=idx, t=total: self.log(f"[{i}/{t}] 正在下载: {f}...", "INFO"))
            
            try:
                req = urllib.request.Request(download_url, headers={"User-Agent": "DuiPai-Tool"})
                # 如果有 token，也需要加在 header 里
                token = self.gh_token_var.get().strip()
                if token:
                    req.add_header("Authorization", f"token {token}")

                with urllib.request.urlopen(req, timeout=30) as response, open(save_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                success_count += 1
                self.root.after(0, lambda f=filename: self.log(f"✓ 下载成功: {f}", "SUCCESS"))
                
            except Exception as e:
                fail_count += 1
                self.root.after(0, lambda f=filename, err=str(e): self.log(f"✗ 下载失败 {f}: {err}", "ERROR"))

        # 全部完成后
        self.root.after(0, self._on_batch_download_finish, success_count, fail_count, save_dir)

    def _on_batch_download_finish(self, success_count, fail_count, save_dir):
        """批量下载完成回调"""
        self.btn_gh_download.config(state="normal")
        
        msg = f"批量下载完成！\n成功: {success_count} 个\n失败: {fail_count} 个\n保存路径: {save_dir}"
        
        if success_count > 0:
            # 自动更新主界面配置（取第一个成功的文件作为 Gen）
            # 你可以在这里添加逻辑，比如自动填入第一个下载的文件到 Gen 配置
            pass
            
        messagebox.showinfo("下载完成", msg)
        self.log(f"=== 批量下载结束 (成功:{success_count}, 失败:{fail_count}) ===", "SUCCESS")

    def _on_download_success(self, save_path, filename):
        """下载成功回调"""
        self.log(f"✓ 下载成功: {save_path}", "SUCCESS")
        
        # 自动更新主界面的 Gen 路径和文件名
        self.gen_dir_var.set(os.path.dirname(save_path))
        self.gen_file_var.set(filename)
        self.use_gen_var.set(True)  # 自动勾选使用生成器
        
        self.btn_gh_download.config(state="normal")
        messagebox.showinfo("成功", f"文件已下载并自动配置为数据生成器！\n路径: {save_path}")

    def create_widgets(self):
        # --- 1. 文件配置 ---
        frame_top = ttk.LabelFrame(self.main_scrollable_frame, text=" 1. 文件配置 (输入前缀后按回车自动填充) ", padding=15)
        frame_top.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(frame_top, text="文件前缀:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.prefix_entry = ttk.Entry(frame_top, textvariable=self.prefix_var, width=25)
        self.prefix_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.prefix_entry.bind('<Return>', self.auto_fill_filenames)
        
        ttk.Checkbutton(frame_top, text="使用数据生成器 (Gen)", variable=self.use_gen_var, 
                       command=self.toggle_gen_input).grid(row=0, column=2, padx=15)
        ttk.Checkbutton(frame_top, text="对拍成功后自动清理临时文件", variable=self.auto_clean_var).grid(row=0, column=3, padx=10)

        # --- 2. 路径与文件名 ---
        frame_paths = ttk.LabelFrame(self.main_scrollable_frame, text=" 2. 文件夹路径 & 文件名 ", padding=15)
        frame_paths.pack(fill="x", padx=15, pady=10)
        
        self.create_file_row(frame_paths, "待测程序 (Test):", self.test_dir_var, self.test_file_var, 0)
        self.create_file_row(frame_paths, "标准程序 (Demo):", self.demo_dir_var, self.demo_file_var, 1)
        
        self.gen_row_frame = ttk.Frame(frame_paths)
        self.create_file_row(self.gen_row_frame, "数据生成 (Gen):", self.gen_dir_var, self.gen_file_var, 0)
        self.gen_row_frame.grid(row=2, column=0, columnspan=5, sticky="ew", pady=5)
        
        # --- 3. 对拍参数 ---
        frame_params = ttk.LabelFrame(self.main_scrollable_frame, text=" 3. 对拍参数 ", padding=15)
        frame_params.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(frame_params, text="txt_compare 参数:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(frame_params, textvariable=self.compare_args_var, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(frame_params, text="(例: --max_line 541 --trim all)", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        frame_sub = ttk.Frame(frame_params)
        frame_sub.grid(row=1, column=0, columnspan=4, sticky="w", pady=10)
        
        ttk.Label(frame_sub, text="对拍次数:").pack(side="left", padx=5)
        ttk.Entry(frame_sub, textvariable=self.times_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(frame_sub, text="单点时限(秒):").pack(side="left", padx=20)
        ttk.Entry(frame_sub, textvariable=self.time_limit_var, width=10).pack(side="left", padx=5)
        
        # 在 frame_params 定义之后添加
        self.create_github_frame(self.main_scrollable_frame)
        
        # --- 按钮区 ---
        frame_btn = ttk.Frame(self.main_scrollable_frame)
        frame_btn.pack(fill="x", padx=15, pady=10)
        
        self.btn_start = ttk.Button(frame_btn, text="开始对拍", command=self.start_duipai)
        self.btn_start.pack(side="left", padx=20)
        
        self.btn_stop = ttk.Button(frame_btn, text="停止", command=self.stop_duipai, state="disabled")
        self.btn_stop.pack(side="left", padx=20)
        
        ttk.Button(frame_btn, text="清空日志", command=lambda: self.log_text.delete('1.0', 'end')).pack(side="right", padx=20)
        ttk.Button(frame_btn, text="保存配置", command=self.save_current_config).pack(side="right", padx=10)

        # --- 日志区 ---
        frame_log = ttk.LabelFrame(self.main_scrollable_frame, text=" 运行日志 ", padding=10)
        frame_log.pack(fill="both", expand=True, padx=15, pady=10)
        
        # 使用等宽字体，避免中文字体问题
        try:
            self.log_text = scrolledtext.ScrolledText(frame_log, height=18, state='disabled', 
                                                      font=("Consolas", 16), wrap=tk.WORD)
        except:
            self.log_text = scrolledtext.ScrolledText(frame_log, height=18, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        
        # 设置颜色标签
        self.log_text.tag_config("INFO", foreground="#000000")
        self.log_text.tag_config("SUCCESS", foreground="#008000")
        self.log_text.tag_config("ERROR", foreground="#DC143C")
        self.log_text.tag_config("WARNING", foreground="#FF8C00")
        self.log_text.tag_config("CMD", foreground="#0000CD")
        self.log_text.tag_config("PATH", foreground="#4169E1")
        
        self.log_text.bind("<MouseWheel>", lambda e: "break" if self.log_text.compare("end", "==", "1.0") else None)
        
        frame_paths.columnconfigure(1, weight=1)
        frame_params.columnconfigure(1, weight=1)
        
    def create_file_row(self, parent, label_text, dir_var, file_var, row):
        ttk.Label(parent, text=label_text, width=16).grid(row=row, column=0, sticky="e", pady=5, padx=5)
        
        dir_entry = ttk.Entry(parent, textvariable=dir_var, width=45)
        dir_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(parent, text="浏览...", command=lambda: self.browse_folder(dir_var), width=8).grid(row=row, column=2, pady=5, padx=5)
        
        ttk.Label(parent, text="文件名:").grid(row=row, column=3, sticky="e", padx=10)
        file_entry = ttk.Entry(parent, textvariable=file_var, width=25)
        file_entry.grid(row=row, column=4, sticky="w", pady=5)
        
        parent.columnconfigure(1, weight=1)

    def auto_fill_filenames(self, event=None):
        prefix = self.prefix_var.get().strip()
        if not prefix:
            return
        
        self.test_file_var.set(f"{prefix}.exe")
        self.demo_file_var.set(f"{prefix}-demo.exe")
        self.gen_file_var.set(f"{prefix}-gen.exe")
        
        self.log(f"已根据前缀 '{prefix}' 自动填充文件名", "SUCCESS")

    def browse_folder(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def toggle_gen_input(self):
        if self.use_gen_var.get():
            self.gen_row_frame.grid()
        else:
            self.gen_row_frame.grid_remove()

    def log(self, message, tag="INFO"):
        self.msg_queue.put((message, tag))

    def check_queue(self):
        try:
            while True:
                message, tag = self.msg_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert('end', message + "\n", tag)
                self.log_text.see('end')
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def get_full_path(self, dir_var, file_var):
        """获取完整路径 - 确保读取最新值"""
        if not dir_var.get() or not file_var.get():
            return None
        return os.path.join(dir_var.get(), file_var.get())

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
            "gh_token": self.gh_token_var.get(),
            "gh_url": self.gh_url_var.get(),
            "gh_branch": self.gh_branch_var.get(),
            "gh_save_dir": self.gh_save_dir_var.get(),
            "gh_proxy": self.gh_proxy_var.get(),
        }
        self.config.save_config(data)
        messagebox.showinfo("成功", "配置已保存！")
        self.log("配置已保存到 duipai_config.json", "SUCCESS")

    def on_closing(self):
        """窗口关闭时自动保存配置"""
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
            "gh_token": self.gh_token_var.get(),
            "gh_url": self.gh_url_var.get(),
            "gh_branch": self.gh_branch_var.get(),
            "gh_save_dir": self.gh_save_dir_var.get(),
            "gh_proxy": self.gh_proxy_var.get(),
        }
        self.config.save_config(data)
        self.root.destroy()

    def start_duipai(self):
        if self.running:
            return
            
        # ✅ 关键：在点击开始时，实时获取当前输入框的值
        current_test_file = self.test_file_var.get()
        current_demo_file = self.demo_file_var.get()
        current_gen_file = self.gen_file_var.get()
        
        # 调试日志：显示实际查找的文件名
        self.log(f"\n[调试] 当前文件名设置:", "INFO")
        self.log(f"  Test: {current_test_file}", "PATH")
        self.log(f"  Demo: {current_demo_file}", "PATH")
        self.log(f"  Gen:  {current_gen_file}", "PATH")
        
        test_file = self.get_full_path(self.test_dir_var, self.test_file_var)
        demo_file = self.get_full_path(self.demo_dir_var, self.demo_file_var)
        gen_file = None
        
        if self.use_gen_var.get():
            gen_file = self.get_full_path(self.gen_dir_var, self.gen_file_var)

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
        self.log(f"参数设置: {self.compare_args_var.get()}")
        self.log(f"对拍次数: {self.times_var.get()} | 时限: {self.time_limit_var.get()}秒")
        if self.auto_clean_var.get():
            self.log("模式: 开启自动清理临时文件", "WARNING")
        self.log("=" * 60, "CMD")
        
        t = threading.Thread(target=self.run_loop, args=(test_file, demo_file, gen_file))
        t.daemon = True
        t.start()

    def stop_duipai(self):
        self.running = False
        self.log("用户停止对拍...", "WARNING")

    def run_loop(self, test_exe, demo_exe, gen_exe):
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
            
            if gen_exe:
                gen_dir = os.path.dirname(gen_exe)
                
                if self.auto_clean_var.get():
                    try:
                        all_files_before = set(os.listdir(gen_dir))
                    except Exception:
                        self.auto_clean_var.set(False)
                        self.log("无法读取生成器目录，自动清理已禁用", "WARNING")
                        all_files_before = set()
                else:
                    all_files_before = set()

                cmd_gen = self.logic.get_run_command(gen_exe)
                status, err = self.logic.run_program(cmd_gen, None, temp_in, time_limit)
                
                if status != "AC":
                    self.log(f"  [Gen] {status}: {err}", "ERROR")
                    global_success = False
                    break
                
                if self.auto_clean_var.get() and all_files_before:
                    try:
                        all_files_after = set(os.listdir(gen_dir))
                        generated_files = all_files_after - all_files_before
                        generated_files = {f for f in generated_files if not f.startswith('~$')} 
                        self.gen_files_generated = generated_files
                        if generated_files:
                            self.log(f"  [Clean] 检测到 {len(generated_files)} 个新文件", "INFO")
                    except Exception:
                        pass

            else:
                if not os.path.exists(temp_in):
                    self.log(f"  [Warn] 未找到 {temp_in}", "WARNING")

            cmd_demo = self.logic.get_run_command(demo_exe)
            status_std, err_std = self.logic.run_program(cmd_demo, temp_in, temp_std_out, time_limit)
            if status_std != "AC":
                self.log(f"  [Demo] {status_std}: {err_std}", "ERROR")
                global_success = False
                break
            
            cmd_test = self.logic.get_run_command(test_exe)
            status_test, err_test = self.logic.run_program(cmd_test, temp_in, temp_test_out, time_limit)
            if status_test != "AC":
                self.log(f"  [Test] {status_test}: {err_test}", "ERROR")
                global_success = False
                break
            
            is_same, diff_info = self.logic.compare_files(temp_std_out, temp_test_out, compare_args)
            
            if not is_same:
                self.log(f"  [WA] 发现不同!", "ERROR")
                self.log(f"  差异:\n{diff_info}", "ERROR")
                self.log(f">>> 保留现场文件", "WARNING")
                global_success = False
                break
            else:
                if i % 10 == 0 or i == times:
                    self.log(f"  [OK] 已通过 {i} 组", "SUCCESS")

        if self.running:
            if global_success:
                self.log("\n" + "=" * 60, "SUCCESS")
                self.log("           对拍全部通过!", "SUCCESS")
                self.log("=" * 60, "SUCCESS")
                self.clean_generated_files()
            else:
                self.log("\n" + "=" * 60, "ERROR")
                self.log("           对拍失败", "ERROR")
                self.log("=" * 60, "ERROR")
        else:
             self.log("\n对拍已中断", "WARNING")
             
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def clean_generated_files(self):
        if not self.auto_clean_var.get():
            return
        if not self.gen_files_generated:
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
        
        self.log(f"清理完成，删除 {count} 个文件", "SUCCESS")
        self.gen_files_generated.clear()