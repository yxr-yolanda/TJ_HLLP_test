# -*- coding: utf-8 -*-
"""配置管理器 - 支持打包后路径"""
import os
import sys
import json

class ConfigManager:
    """配置文件管理器"""
    
    DEFAULT_CONFIG = {
        # 基础配置
        "prefix": "",
        "test_dir": "",
        "demo_dir": "",
        "gen_dir": "",
        "test_file": ".exe",
        "demo_file": "-demo.exe",
        "gen_file": "-gen.exe",
        "use_gen": True,
        "auto_clean": False,
        "compare_args": "--max_line 0",
        "times": "100",
        "time_limit": "1.0",
        
        # 子文件夹配置（仅 Test 生效）
        "test_use_subfolder": False,
        "test_subfolder": "",
        
        # GitHub 配置
        "gh_token": "",
        "gh_url": "https://github.com/",
        "gh_branch": "main",
        "gh_save_dir": "",
        "gh_proxy": ""
    }
    
    def __init__(self, config_file="duipai_config.json"):
        # 兼容 PyInstaller 打包
        if getattr(sys, 'frozen', False):
            self.config_file = os.path.join(os.path.dirname(sys.executable), config_file)
        else:
            self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        config = self.DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    config.update(saved)
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")
        return config
    
    def save_config(self, data):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value