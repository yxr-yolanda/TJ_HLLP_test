#include <iostream>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <string>

using namespace std;

// 配置文件名
const string STATE_FILE = "gen_state.txt";   // 记录当前生成到了哪个数
const string DEBUG_FILE = "gen_debug.log";   // 记录生成的详细数据（备份）

int main() {
    // 初始化随机数种子
    srand(time(NULL));

    // 1. 读取当前进度
    int current_idx = 0; // 0 对应 -10, 1 对应 -9, ..., 75 对应 65
    ifstream fin_state(STATE_FILE);
    if (fin_state.is_open()) {
        fin_state >> current_idx;
        fin_state.close();
    }

    // 2. 计算本次的目标合法值
    int target_val = current_idx - 10;

    // 如果超出范围 (+65 是第 75 个索引，即 75-10=65)，则重置为 -10 循环
    if (target_val > 65) {
        current_idx = 0;
        target_val = -10;
        // 也可以选择直接 return 0; 来停止生成
    }

    // 3. 打开调试日志文件
    ofstream fout_debug(DEBUG_FILE, ios::app);
    fout_debug << "=== Run #" << (current_idx + 1) << " ===" << endl;
    fout_debug << "Target Valid Value: " << target_val << endl;

    // 4. 生成随机数量的非法输入 (0 到 3 个)
    // 这样可以测试程序的“输入非法，请重新输入”逻辑
    int num_illegal = rand() % 4; 
    
    for (int i = 0; i < num_illegal; i++) {
        int illegal_val;
        // 50% 概率生成太小的数，50% 概率生成太大的数
        if (rand() % 2 == 0) {
            // 范围 [-100, -11]
            illegal_val = -(rand() % 90 + 11); 
        } else {
            // 范围 [66, 200]
            illegal_val = rand() % 135 + 66;
        }
        
        // 【关键】输出到标准输出，供被测程序读取
        cout << illegal_val << endl;
        
        // 记录到日志
        fout_debug << "  Illegal Input: " << illegal_val << endl;
    }

    // 5. 输出最终的合法值
    // 这是这一轮生成的“最后一个数”
    cout << target_val << endl;
    fout_debug << "  Valid Input:   " << target_val << endl;
    fout_debug << endl; // 空行分隔
    fout_debug.close();

    // 6. 更新进度状态
    current_idx++;
    ofstream fout_state(STATE_FILE);
    fout_state << current_idx;
    fout_state.close();

    return 0;
}