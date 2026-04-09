import os
import subprocess
import sys

# 隐藏控制台窗口
if sys.platform == 'win32':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    startupinfo = None

class DuiPaiLogic:
    def __init__(self):
        self.TIME_LIMIT = 2.0
        self.FILE_ENCODING = 'gbk'

    def get_run_command(self, file_path):
        if not os.path.exists(file_path): return None
        if file_path.endswith(".exe"): return [file_path]
        if file_path.endswith(".py"): return ["python", file_path]
        return [file_path]

    def run_program(self, cmd, input_file, output_file, timeout):
        try:
            stdin_handle = subprocess.PIPE
            if input_file and os.path.exists(input_file):
                stdin_handle = open(input_file, 'r', encoding=self.FILE_ENCODING, errors='ignore')
            stdout_handle = open(output_file, 'w', encoding=self.FILE_ENCODING) if output_file else subprocess.PIPE

            process = subprocess.Popen(cmd, stdin=stdin_handle, stdout=stdout_handle,
                                       stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
            try:
                _, stderr = process.communicate(timeout=timeout)
                if hasattr(stdin_handle, 'close'): stdin_handle.close()
                if hasattr(stdout_handle, 'close'): stdout_handle.close()
                if process.returncode != 0:
                    err = ""
                    try: err = stderr.decode('gbk')
                    except: 
                        try: err = stderr.decode('gbk')
                        except: err = stderr.decode('gbk', errors='ignore')
                    return "RE", f"返回值：{process.returncode}\n{err}"
                return "AC", None
            except subprocess.TimeoutExpired:
                process.kill()
                return "TLE", f"运行超过 {timeout} 秒"
        except Exception as e:
            return "ERR", str(e)

    def compare_files(self, file1, file2, txt_compare_args, max_lines=0):
        cmd = ["txt_compare", "--file1", file1, "--file2", file2]
        args_list = txt_compare_args.split() if isinstance(txt_compare_args, str) else txt_compare_args
        cmd.extend(args_list)
        if not any("--max_line" in arg for arg in args_list) and max_lines > 0:
            cmd.extend(["--max_line", str(max_lines)])
        cmd.extend(["--display", "detailed"])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding=self.FILE_ENCODING,
                                 errors='ignore', startupinfo=startupinfo)
            output = (res.stdout or res.stderr).strip()
            return (True, "") if "在指定检查条件下完全一致" in output else (False, output)
        except FileNotFoundError:
            return False, "错误：找不到 txt_compare 工具。"
        except Exception as e:
            return False, f"比对工具运行错误：{str(e)}"