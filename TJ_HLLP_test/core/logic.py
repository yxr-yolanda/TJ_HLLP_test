# -*- coding: utf-8 -*-
"""对拍核心逻辑 - 无 GUI 依赖"""
import os
import subprocess
import sys

# Windows 隐藏控制台
if sys.platform == 'win32':
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    STARTUP_INFO = None

class DuiPaiLogic:
    """对拍业务逻辑"""
    
    def __init__(self, time_limit=2.0, encoding='gbk'):
        self.TIME_LIMIT = time_limit
        self.ENCODING = encoding
    
    def get_run_command(self, file_path):
        """获取程序运行命令"""
        if not os.path.exists(file_path):
            return None
        if file_path.endswith(".exe"):
            return [file_path]
        elif file_path.endswith(".py"):
            return ["python", file_path]
        return [file_path]
    
    def run_program(self, cmd, input_file, output_file, timeout=None):
        """运行程序并捕获结果"""
        timeout = timeout or self.TIME_LIMIT
        try:
            # 处理输入输出文件
            stdin = subprocess.PIPE
            if input_file and os.path.exists(input_file):
                stdin = open(input_file, 'r', encoding=self.ENCODING, errors='ignore')
            
            stdout = subprocess.PIPE
            if output_file:
                stdout = open(output_file, 'w', encoding=self.ENCODING)
            
            process = subprocess.Popen(
                cmd, 
                stdin=stdin, 
                stdout=stdout, 
                stderr=subprocess.PIPE,
                shell=False, 
                startupinfo=STARTUP_INFO
            )
            
            try:
                _, stderr = process.communicate(timeout=timeout)
                
                if hasattr(stdin, 'close'): 
                    stdin.close()
                if hasattr(stdout, 'close'): 
                    stdout.close()
                
                if process.returncode != 0:
                    err = self._decode(stderr)
                    return "RE", f"返回值：{process.returncode}\n{err}"
                return "AC", None
                
            except subprocess.TimeoutExpired:
                process.kill()
                return "TLE", f"运行超过 {timeout} 秒"
                
        except Exception as e:
            return "ERR", str(e)
    
    def compare_files(self, file1, file2, args, max_lines=0):
        """调用 txt_compare 比对文件"""
        cmd = ["txt_compare", "--file1", file1, "--file2", file2]
        
        if isinstance(args, str):
            args_list = args.split()
        else:
            args_list = args
        cmd.extend(args_list)
        
        if "--max_line" not in str(cmd) and max_lines > 0:
            cmd.extend(["--max_line", str(max_lines)])
        cmd.extend(["--display", "detailed"])
        
        try:
            res = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                encoding=self.ENCODING, 
                errors='ignore', 
                startupinfo=STARTUP_INFO
            )
            output = (res.stdout or res.stderr).strip()
            
            if "在指定检查条件下完全一致" in output:
                return True, ""
            return False, output
            
        except FileNotFoundError:
            return False, "❌ 找不到 txt_compare 工具"
        except Exception as e:
            return False, f"❌ 比对失败: {e}"
    
    def _decode(self, data):
        """尝试多种编码解码"""
        if not data:
            return ""
        for enc in ['gbk', 'utf-8', 'gb2312']:
            try:
                return data.decode(enc)
            except:
                continue
        return data.decode('gbk', errors='ignore')