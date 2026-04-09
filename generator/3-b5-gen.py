# -*- coding: utf-8 -*-
import random
import sys
import os

# 配置
LOG_FILE = "test_case_log.txt"

def is_leap(year):
    """判断闰年"""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_max_day(year, month):
    """获取某年某月的最大天数"""
    if month == 2:
        return 29 if is_leap(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

def solve(y, m, d):
    """计算期望输出（与被测程序逻辑一致）"""
    # 1. 检查月份
    if m < 1 or m > 12:
        return "输入错误-月份不正确"
    
    # 2. 检查日期
    max_d = get_max_day(y, m)
    if d < 1 or d > max_d:
        return "输入错误-日与月的关系非法"
    
    # 3. 计算天数
    days = 0
    for i in range(1, m):
        days += get_max_day(y, i)
    days += d
    
    return f"{y}-{m}-{d}是{y}年的第{days}天"

def generate_corner_case():
    """生成 Corner Case（边界/错误情况）"""
    # 定义一些典型的 Corner Case 模板
    # (year_range, month_range, day_range, description)
    # 为了简化，这里直接列举具体的种子数据，或者随机生成特定的边界值
    
    cases = [
        # 闰年边界
        (2024, 2, 29, "闰年2月29-合法"),
        (2000, 2, 29, "世纪闰年2月29-合法"),
        (1900, 2, 29, "世纪平年2月29-非法日"),
        
        # 平年边界
        (2023, 2, 28, "平年2月28-合法"),
        (2023, 2, 29, "平年2月29-非法日"),
        
        # 月份错误 (优先级测试：月错 > 日错)
        (2023, 0, 1, "月=0-非法月"),
        (2023, 13, 1, "月=13-非法月"),
        (2023, 13, 32, "月日双错-应报月错"), # 关键测试点
        
        # 日期错误
        (2023, 1, 0, "日=0-非法日"),
        (2023, 1, 32, "日=32-非法日"),
        (2023, 4, 31, "小月31-非法日"),
        (2023, 6, 31, "小月31-非法日"),
        
        # 负数年份 (题目要求：年只判断闰年，不考范围，包括负数)
        (-2024, 2, 29, "负数闰年2月29-合法"),
        (-2023, 2, 29, "负数平年2月29-非法日"),
    ]
    
    return random.choice(cases)

def generate_random_case():
    """生成完全随机的 Case"""
    # 年份：随机范围，包含负数和大数
    y = random.choice([
        random.randint(1900, 2100), # 正常
        random.randint(2000, 9999), # 大数
        random.randint(-1000, -1),  # 负数
        random.choice([1900, 2000, 2100, 2400]) # 世纪年
    ])
    
    # 月份：大概率合法，小概率非法
    if random.random() < 0.2:
        m = random.choice([0, 13, -5, 100])
    else:
        m = random.randint(1, 12)
        
    # 日期：大概率合法，小概率非法
    if 1 <= m <= 12:
        max_d = get_max_day(y, m)
        if random.random() < 0.2:
            d = random.choice([0, max_d + 1, 32, -1])
        else:
            d = random.randint(1, max_d)
    else:
        d = random.randint(1, 31) # 月都错了，日随便给
        
    return y, m, d, "Random"

def main():
    # 30% 概率出 Corner Case，70% 概率出随机数据
    if random.random() < 0.3:
        y, m, d, desc = generate_corner_case()
        case_type = "Corner"
    else:
        y, m, d, desc = generate_random_case()
        case_type = "Random"
    
    # 计算期望结果
    expected = solve(y, m, d)
    
    # 1. 标准输出：只输出三个数字，空格隔开
    print(f"{y} {m} {d}")
    
    # 2. 文件输出：记录详细信息，方便对拍核对
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{case_type}] Input: {y} {m} {d} | Expected: {expected} | Desc: {desc}\n")

if __name__ == "__main__":
    main()