# -*- coding: utf-8 -*-
import random
import sys

def generate_random():
    """
    生成 [0.01, 99.99] 之间的随机浮点数
    通过生成整数分再除以100来避免浮点精度问题
    """
    # 范围是 1分 到 9999分 (99.99元)
    cents = random.randint(1, 9999)
    return cents / 100.0

def generate_corner():
    """
    生成边界情况 (Corner Cases)
    包括：最小值、最大值、整数、刚好需要/不需要某种硬币的边界
    """
    cases = [
        0.01, 0.02, 0.03, 0.04, 0.05,  # 分位边界 (测试 1分, 2分, 5分)
        0.09, 0.10, 0.11, 0.15,         # 角位边界 (测试 1角)
        0.49, 0.50, 0.51,               # 5角边界
        0.99, 1.00, 1.01,               # 元位进位
        4.99, 5.00, 5.01,               # 5元边界
        9.99, 10.00, 10.01,             # 10元边界
        19.99, 20.00, 20.01,            # 20元边界
        49.99, 50.00, 50.01,            # 50元边界
        99.98, 99.99                    # 最大值边界
    ]
    return random.choice(cases)

if __name__ == "__main__":
    mode = "random"
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "corner":
            mode = "corner"
        elif arg == "mix":
            mode = "mix"
    
    val = 0.0
    
    if mode == "random":
        val = generate_random()
    elif mode == "corner":
        val = generate_corner()
    elif mode == "mix":
        # 20% 概率生成边界数据，80% 概率生成随机数据
        if random.random() < 0.2:
            val = generate_corner()
        else:
            val = generate_random()
            
    # 格式化输出：强制保留两位小数
    # 例如 0.1 会输出 0.10, 5 会输出 5.00
    # print(0)
    print(f"{val:.2f}")