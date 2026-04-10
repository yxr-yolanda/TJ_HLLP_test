#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <climits>

using namespace std;

// 生成随机字符串（纯字母或标点）
string random_garbage() {
    string s = "";
    int len = rand() % 5 + 1; // 长度 1-5
    for (int i = 0; i < len; i++) {
        // 随机生成字母或符号
        char c = rand() % 2 == 0 ? (rand() % 26 + 'a') : (rand() % 10 + '!'); 
        s += c;
    }
    return s;
}

// 生成非法数字（范围错误或溢出）
string random_bad_number() {
    int type = rand() % 3;
    if (type == 0) {
        // 负数
        return to_string(-(rand() % 1000 + 1));
    } else if (type == 1) {
        // 大于 100 但不过溢
        return to_string(rand() % 900 + 101);
    } else {
        // 溢出 (超过 int 范围)
        // 生成一个很长的数字串
        string s = "";
        int len = rand() % 10 + 11; // 长度 11-20
        for(int i=0; i<len; i++) {
            s += to_string(rand() % 10);
        }
        return s;
    }
}

int main() {
    // 使用当前时间作为随机种子
    srand((unsigned)time(NULL));

    // 随机决定生成多少行错误数据 (5 到 15 行)
    int error_lines = rand() % 11 + 5;

    for (int i = 0; i < error_lines; i++) {
        int mode = rand() % 5; // 5种错误模式

        switch (mode) {
            case 0: // 纯垃圾字符 (触发 cin fail)
                cout << random_garbage() << endl;
                break;

            case 1: // 纯非法数字 (触发逻辑错误或溢出)
                cout << random_bad_number() << endl;
                break;

            case 2: // 数字(非法) + 字符 (先读数字报错，再读字符报错)
                cout << random_bad_number() << random_garbage() << endl;
                break;

            case 3: // 字符 + 数字(非法) (先读字符报错，再读数字报错)
                cout << random_garbage() << random_bad_number() << endl;
                break;
            
            case 4: // 空格分隔的多个非法数字
                // 生成 2-3 个非法数字，用空格隔开
                cout << random_bad_number();
                int spaces = rand() % 2 + 1;
                for(int k=0; k<spaces; k++) {
                    cout << " " << random_bad_number();
                }
                cout << endl;
                break;
        }
    }

    // 最后必须输出一个合法数字 [0, 100] 让程序正常结束
    cout << (rand() % 101) << endl;

    return 0;
}