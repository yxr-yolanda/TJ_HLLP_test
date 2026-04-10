# -*- coding: utf-8 -*-
"""GitHub 文件下载面板"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import urllib.request
import urllib.parse
import urllib.error

class GitHubPanel(ttk.LabelFrame):
    """GitHub 下载功能面板"""
    
    def __init__(self, parent, log_callback=None, on_cloud_duipai=None, **kwargs):
        super().__init__(parent, text=" 4. 从 GitHub 下载数据生成器 ", **kwargs)
        self.log_callback = log_callback
        self.on_cloud_duipai = on_cloud_duipai
        self._setup_vars()
        self._create_widgets()
    
    def _setup_vars(self):
        self.token_var = tk.StringVar()
        self.url_var = tk.StringVar(value="https://github.com/")
        self.branch_var = tk.StringVar(value="main")
        self.proxy_var = tk.StringVar()
        self.save_dir_var = tk.StringVar()
        
        self.check_vars = []
        self.file_data_map = {}
        self.btn_download = None
        self.canvas = None
        self.scroll_frame = None
    
    def _create_widgets(self):
        # 配置网格
        self.columnconfigure(1, weight=1)
        # ✅ 让第 3 行（文件列表区域）可以自动伸缩
        self.rowconfigure(3, weight=1)
        
        # Token + 分支
        ttk.Label(self, text="GitHub Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.token_var, show="*").grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(self, text="分支:").grid(row=0, column=2, sticky="e", padx=5)
        ttk.Entry(self, textvariable=self.branch_var, width=10).grid(row=0, column=3, sticky="w", padx=5)
        
        # 代理
        ttk.Label(self, text="代理:").grid(row=1, column=0, sticky="e", padx=5)
        ttk.Entry(self, textvariable=self.proxy_var).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Label(self, text="(例: http://127.0.0.1:7890)", foreground="gray").grid(
            row=1, column=2, columnspan=2, sticky="w"
        )
        
        # 仓库链接 + 获取按钮
        ttk.Label(self, text="仓库链接:").grid(row=2, column=0, sticky="e", padx=5)
        ttk.Entry(self, textvariable=self.url_var).grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Button(self, text="获取文件列表", command=self.fetch_files).grid(
            row=2, column=2, columnspan=2, padx=5, sticky="ew"
        )
        
        # 文件列表区域
        ttk.Label(self, text="仓库文件:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self._create_file_list()
        
        # 保存路径 + 下载按钮
        ttk.Label(self, text="保存到:").grid(row=4, column=0, sticky="e", padx=5)
        ttk.Entry(self, textvariable=self.save_dir_var).grid(row=4, column=1, sticky="ew", padx=5)
        ttk.Button(self, text="浏览...", command=self._browse_save_dir).grid(row=4, column=2, padx=5)
        
        self.btn_download = ttk.Button(
            self, text="下载选中 (0)", command=self.download_selected, state="disabled"
        )
        self.btn_download.grid(row=4, column=3, padx=5, pady=5)
        # ✅ 新增：云端自动对拍按钮
        self.btn_cloud = ttk.Button(self, text="☁️ 云端自动对拍 (1.in ~ N.in)", 
                                    command=self._trigger_cloud_duipai)
        self.btn_cloud.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
    
    def get_repo_info(self):
        """解析当前 GitHub 链接，返回 owner, repo, branch, subpath"""
        url = self.url_var.get().strip()
        if not url.startswith("http"): url = "https://" + url
        
        parsed = urllib.parse.urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        if parts and parts[0] == "github.com": parts = parts[1:]
        if len(parts) < 2: return None
        
        owner, repo = parts[0], parts[1]
        branch = self.branch_var.get().strip() or "main"
        
        subpath = ""
        if len(parts) > 2:
            if parts[2] == 'tree' and len(parts) > 4: subpath = "/".join(parts[4:])
            elif parts[2] != 'tree': subpath = "/".join(parts[2:])
        return owner, repo, branch, subpath

    def get_opener(self):
        """构建支持代理和 Token 的 Opener（供主程序调用）"""
        handlers = []
        
        # 处理代理
        proxy_url = self.proxy_var.get().strip()
        if proxy_url:
            handlers.append(urllib.request.ProxyHandler({
                'http': proxy_url, 
                'https': proxy_url
            }))
        
        # 处理 Token
        token = self.token_var.get().strip()
        if token:
            class TokenHandler(urllib.request.BaseHandler):
                def __init__(self, token_str):
                    super().__init__()
                    self.token = token_str
                
                def http_request(self, req):
                    req.add_header("Authorization", f"token {self.token}")
                    req.add_header("User-Agent", "DuiPai-Tool")
                    return req
                
                https_request = http_request
            handlers.append(TokenHandler(token))
        else:
            class UAHandler(urllib.request.BaseHandler):
                def http_request(self, req):
                    req.add_header("User-Agent", "DuiPai-Tool")
                    return req
                https_request = http_request
            handlers.append(UAHandler())

        return urllib.request.build_opener(*handlers)

    def _trigger_cloud_duipai(self):
        """按钮点击触发"""
        if self.on_cloud_duipai:
            self.on_cloud_duipai()

    def _create_file_list(self):
        """创建可滚动的复选框列表"""
        container = ttk.Frame(self, relief="sunken", borderwidth=1)
        container.grid(row=3, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # ✅ 增加 Canvas 的初始高度
        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0, 
                                height=150)  # 从 150 增加到 250
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        # 创建窗口
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # ✅ 绑定滚轮事件到 canvas 和 container（灰色区域）
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        container.bind("<MouseWheel>", self._on_mousewheel)  # 新增：灰色区域也能滚动
        
        # 绑定配置事件
        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _on_frame_configure(self, event):
        """当内部 frame 大小变化时，更新 scrollregion"""
        # ✅ 获取实际内容区域
        bbox = self.canvas.bbox("all")
        if bbox:
            # bbox 返回 (x1, y1, x2, y2)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            self.canvas.configure(scrollregion=(0, 0, width, height))
        
    def _on_canvas_configure(self, event):
        """当 Canvas 大小变化时，调整内部 frame 的宽度"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """文件列表滚轮：滚动条区域忽略，内容区优先滚动，到头后传递给主窗口"""
        # 1. 检测鼠标是否在滚动条控件上
        toplevel = self.winfo_toplevel()
        widget_under = toplevel.winfo_containing(event.x_root, event.y_root)
        if isinstance(widget_under, (tk.Scrollbar, ttk.Scrollbar)):
            return "break"  # 直接拦截，不滚动画面

        # 2. 正常滚动逻辑
        delta = int(-1 * (event.delta / 120))
        view = self.canvas.yview()
        
        can_scroll = False
        if delta < 0 and view[0] > 0.0:  # 向上滚且没到顶
            can_scroll = True
        elif delta > 0 and view[1] < 1.0:  # 向下滚且没到底
            can_scroll = True
        
        if can_scroll:
            self.canvas.yview_scroll(delta, "units")
            return "break"  # 拦截事件，不传给主窗口
            
        # 无法滚动时不拦截，事件自动冒泡给主窗口
    
    def fetch_files(self):
        """获取文件列表（后台线程）"""
        # 清空旧数据
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.check_vars.clear()
        self.file_data_map.clear()
        
        ttk.Label(self.scroll_frame, text="正在连接 GitHub API，请稍候...").pack(pady=20)
        
        def worker():
            try:
                url = self.url_var.get().strip()
                branch = self.branch_var.get().strip() or "main"
                proxy = self.proxy_var.get().strip()
                token = self.token_var.get().strip()
                
                # 解析 URL
                if not url.startswith("http"):
                    url = "https://" + url
                
                parsed = urllib.parse.urlparse(url)
                path_parts = [p for p in parsed.path.split("/") if p]
                
                if path_parts and path_parts[0] == "github.com":
                    path_parts = path_parts[1:]
                
                if len(path_parts) < 2:
                    raise ValueError("链接太短，无法解析")
                
                owner, repo = path_parts[0], path_parts[1]
                
                # 确定子路径
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
                
                # 日志
                if self.log_callback:
                    self.log_callback(f"正在请求: {api_url}", "INFO")
                
                # 构建 opener
                handlers = []
                if proxy:
                    handlers.append(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}))
                    if self.log_callback:
                        self.log_callback(f"使用代理: {proxy}", "INFO")
                
                if token:
                    class TokenHandler(urllib.request.BaseHandler):
                        def __init__(self, token_str):  # ✅ 添加 __init__ 接收 token
                            super().__init__()
                            self.token = token_str
                        
                        def http_request(self, req):
                            req.add_header("Authorization", f"token {self.token}")  # ✅ 使用 self.token
                            req.add_header("User-Agent", "DuiPai-Tool")
                            return req
                        
                        https_request = http_request
                    
                    handlers.append(TokenHandler(token))  # ✅ 现在可以传入参数了
                else:
                    class UAHandler(urllib.request.BaseHandler):
                        def http_request(self, req):
                            req.add_header("User-Agent", "DuiPai-Tool")
                            return req
                        https_request = http_request
                    handlers.append(UAHandler())
                
                opener = urllib.request.build_opener(*handlers)
                
                # 发起请求
                with opener.open(api_url, timeout=15) as response:
                    raw_data = response.read()
                    data = json.loads(raw_data.decode('utf-8'))
                
                # 更新 UI
                self.after(0, lambda: self._update_list(data))
                
            except urllib.error.HTTPError as e:
                msg = f"GitHub 返回错误代码: {e.code}\n"
                if e.code == 404:
                    msg += "找不到仓库或文件夹"
                elif e.code == 403:
                    msg += "访问被拒绝，请检查 Token 或稍后再试"
                self.after(0, lambda m=msg: self._log_error(m))
            
            except Exception as e:
                self.after(0, lambda err=str(e): self._log_error(f"获取失败: {err}"))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _update_list(self, data):
        """更新文件列表显示"""
        # 清空旧数据
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.check_vars.clear()
        self.file_data_map.clear()
        
        file_count = 0
        for item in data:
            if item['type'] == 'file':
                if item['name'].endswith(('.py', '.cpp', '.c', '.exe', '.java')):
                    var = tk.BooleanVar()
                    self.check_vars.append({'name': item['name'], 'var': var, 'data': item})
                    self.file_data_map[item['name']] = item
                    
                    ttk.Checkbutton(
                        self.scroll_frame, 
                        text=f"{item['name']} ({item['size']} bytes)", 
                        variable=var,
                        command=self._update_btn_text
                    ).pack(anchor="nw", padx=10, pady=2, fill="x")
                    file_count += 1
        
        if file_count == 0:
            ttk.Label(
                self.scroll_frame, 
                text="当前目录下未找到支持的生成器文件"
            ).pack(pady=20)
        
        self._update_btn_text()
        
        # ✅ 强制刷新布局
        self.scroll_frame.update_idletasks()
        
        # 获取内容实际高度
        bbox = self.canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            canvas_height = self.canvas.winfo_height()
            
            # ✅ 如果内容高度小于 Canvas 高度，调整 Canvas 高度
            if content_height < canvas_height and content_height > 0:
                # 设置 Canvas 高度为内容高度（但不小于 100）
                new_height = max(content_height + 10, 100)
                self.canvas.config(height=new_height)
        
        # ✅ 强制滚动到顶部
        self.canvas.yview_moveto(0.0)
    
    def _force_scroll_to_top(self):
        """强制滚动到顶部"""
        # 更新 scrollregion
        bbox = self.canvas.bbox("all")
        if bbox:
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            self.canvas.configure(scrollregion=(0, 0, width, height))
        
        # ✅ 关键修复：强制设置视图位置为顶部
        self.canvas.yview_moveto(0.0)
        
        # ✅ 额外强制刷新（确保生效）
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0.0)
        
        # ✅ 如果内容高度小于 Canvas 高度，强制 Canvas 滚动到顶部
        canvas_height = self.canvas.winfo_height()
        if height < canvas_height:
            # 内容比 Canvas 小，强制从 (0,0) 开始显示
            self.canvas.yview_moveto(0.0)
    
    def _update_btn_text(self):
        count = sum(1 for item in self.check_vars if item['var'].get())
        self.btn_download.config(text=f"下载选中 ({count})")
        self.btn_download.config(state="normal" if count > 0 else "disabled")
    
    def download_selected(self):
        """下载选中的文件"""
        selected = [item for item in self.check_vars if item['var'].get()]
        
        if not selected:
            messagebox.showwarning("提示", "请先勾选要下载的文件")
            return
        
        save_dir = self.save_dir_var.get().strip()
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except:
                messagebox.showerror("错误", "无法创建保存目录")
                return
        
        self.btn_download.config(state="disabled")
        
        def worker():
            total = len(selected)
            success = 0
            fail = 0
            
            for idx, item_info in enumerate(selected, 1):
                filename = item_info['name']
                file_data = item_info['data']
                download_url = file_data['download_url']
                save_path = os.path.join(save_dir, filename)
                
                # 日志
                if self.log_callback:
                    self.log_callback(f"[{idx}/{total}] 正在下载: {filename}...", "INFO")
                
                try:
                    # 构建请求
                    req = urllib.request.Request(download_url, headers={"User-Agent": "DuiPai-Tool"})
                    token = self.token_var.get().strip()
                    if token:
                        req.add_header("Authorization", f"token {token}")
                    
                    with urllib.request.urlopen(req, timeout=30) as response:
                        with open(save_path, 'wb') as f:
                            f.write(response.read())
                    
                    success += 1
                    if self.log_callback:
                        self.log_callback(f"✓ 下载成功: {filename}", "SUCCESS")
                
                except Exception as e:
                    fail += 1
                    if self.log_callback:
                        self.log_callback(f"✗ 下载失败 {filename}: {e}", "ERROR")
            
            # 完成
            self.after(0, lambda: self._on_download_complete(success, fail, save_dir))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _on_download_complete(self, success, fail, save_dir):
        self.btn_download.config(state="normal")
        msg = f"批量下载完成！\n成功: {success} 个\n失败: {fail} 个\n保存路径: {save_dir}"
        messagebox.showinfo("下载完成", msg)
        if self.log_callback:
            self.log_callback(f"=== 批量下载结束 (成功:{success}, 失败:{fail}) ===", "SUCCESS")
    
    def _log_error(self, msg):
        if self.log_callback:
            self.log_callback(msg, "ERROR")
        else:
            print(f"❌ {msg}")
    
    def _browse_save_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.save_dir_var.set(path)
    
    def get_config(self):
        """获取当前配置"""
        return {
            "gh_token": self.token_var.get(),
            "gh_url": self.url_var.get(),
            "gh_branch": self.branch_var.get(),
            "gh_proxy": self.proxy_var.get(),
            "gh_save_dir": self.save_dir_var.get()
        }
    
    def load_config(self, config):
        """加载配置"""
        self.token_var.set(config.get("gh_token", ""))
        self.url_var.set(config.get("gh_url", "https://github.com/"))
        self.branch_var.set(config.get("gh_branch", "main"))
        self.proxy_var.set(config.get("gh_proxy", ""))
        self.save_dir_var.set(config.get("gh_save_dir", ""))