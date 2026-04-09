import os
import sys
import json

class ConfigManager:
    def __init__(self, config_file="duipai_config.json"):
        # 兼容 PyInstaller 打包后的路径
        if getattr(sys, 'frozen', False):
            self.config_file = os.path.join(os.path.dirname(sys.executable), config_file)
        else:
            self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        default_config = {
            "prefix": "", "test_dir": "", "demo_dir": "", "gen_dir": "",
            "test_file": ".exe", "demo_file": "-demo.exe", "gen_file": "-gen.exe",
            "use_gen": True, "auto_clean": False, "compare_args": "--max_line 0",
            "times": "100", "time_limit": "1.0",
            "gh_token": "",
            "gh_url": "https://github.com/",
            "gh_branch": "main",
            "gh_save_dir": ""
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    default_config.update(json.load(f))
            except: pass
        return default_config

    def save_config(self, data):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key, default=None): return self.config.get(key, default)
    def set(self, key, value): self.config[key] = value