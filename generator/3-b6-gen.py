# -*- coding: utf-8 -*-
import random
import sys

# 前24个固定测试数据
fixed_data = [
    "0", "9999999999.90", "9999999999.09", "9900000000",
    "8912003005.78", "2501200350.03", "1203056740.01", "203056740.20",
    "23000056.82", "3051200.72", "301000.35", "10001.34",
    "8070.23", "9876.54", "803.03", "12.30",
    "10.03", "9.30", "7.03", "0.35",
    "0.30", "0.07", "0.03", "9999999999.99"
]

# 额外的测试数据（第25-32个）
extra_data = [
    "1.9", "1099999999", "100001234", "100000000.1",
    "100100003.01", "10000010", "1000000100", "101000010"
]

def generate_random_data():
    """生成随机测试数据"""
    choice = random.randint(0, 10)
    
    if choice == 0:
        # 边界值：0
        return "0"
    elif choice == 1:
        # 边界值：接近100亿
        return str(random.uniform(9999999900, 9999999999.99))
    elif choice == 2:
        # 很小的数
        return str(random.uniform(0.01, 0.99))
    elif choice == 3:
        # 整数
        return str(random.randint(1, 9999999999))
    elif choice == 4:
        # 一位小数
        return "{:.1f}".format(random.uniform(0.1, 9999999999))
    elif choice == 5:
        # 两位小数
        return "{:.2f}".format(random.uniform(0.01, 9999999999.99))
    elif choice == 6:
        # 特殊值：10亿
        return "1000000000"
    elif choice == 7:
        # 特殊值：1亿
        return "100000000"
    elif choice == 8:
        # 特殊值：1万
        return "10000"
    elif choice == 9:
        # 特殊值：100
        return "100"
    else:
        # 特殊值：1
        return "1"

def generate_corner_case():
    """生成corner case"""
    corners = [
        "0",
        "0.01",
        "0.10",
        "1",
        "1.00",
        "9999999999.99",
        "9999999999.00",
        "1000000000",
        "100000000",
        "10000000",
        "1000000",
        "100000",
        "10000",
        "1000",
        "100",
        "10",
        "0.99",
        "9.99",
        "99.99",
        "999.99"
    ]
    return random.choice(corners)

def main():
    # 读取调用计数（从文件）
    count_file = "gen_counter.txt"
    backup_file = "gen_backup.txt"
    
    try:
        with open(count_file, 'r', encoding='gbk') as f:
            count = int(f.read().strip())
    except:
        count = 0
    
    # 增加计数
    count += 1
    
    # 保存计数
    with open(count_file, 'w', encoding='gbk') as f:
        f.write(str(count))
    
    # 生成数据
    if count <= 24:
        # 前24次：固定数据
        data = fixed_data[count - 1]
    elif count <= 32:
        # 第25-32次：额外数据
        data = extra_data[count - 25]
    else:
        # 之后：随机数据或corner case
        if random.random() < 0.3:
            data = generate_corner_case()
        else:
            data = generate_random_data()
    
    # 输出到标准输出
    print(data)
    
    # 备份到文件
    with open(backup_file, 'a', encoding='gbk') as f:
        f.write(f"第{count}次: {data}\n")

if __name__ == "__main__":
    main()