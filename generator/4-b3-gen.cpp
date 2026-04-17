#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>
#include <sstream>
#include <iomanip>

using namespace std;

// 图一中可提取的合法【年, 月】组合（去重后用于前几次测试）
// 注意：原题图一是日期，我们取其中的年月部分作为合法输入
vector<pair<int, int>> fig1_valid_ym = {
    {1900, 1},   // 1900.1.1
    {1900, 2},   // 1900.2.28
    {1900, 12},  // 1900.12.31
    {2000, 1},   // 2000.1.15
    {2000, 2},   // 2000.2.28 / 2000.2.29
    {2000, 4},   // 2000.4.13
    {2012, 2},   // 2012.2.29
    {2013, 7},   // 2013.7.12
    {2014, 2},   // 2014.2.28
    {2014, 3},   // 2014.3.6
    {2014, 4},   // 2014.4.7
    {2018, 11},  // 2018.11.1
    {2099, 12}   // 2099.12.31
};

// 非法年月组合（用于错误输入）
vector<pair<int, int>> fig1_invalid_ym = {
    // 无直接非法年月，但我们构造一些
};

bool isLeap(int year) {
    return (year % 400 == 0) || (year % 4 == 0 && year % 100 != 0);
}

int getDaysInMonth(int year, int month) {
    int days[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2 && isLeap(year)) return 29;
    return days[month];
}

int randInt(int min, int max) {
    return rand() % (max - min + 1) + min;
}

string generateErrorLine() {
    int type = rand() % 6;
    stringstream ss;

    switch (type) {
        case 0: // 纯字符或混合
            if (rand() % 2 == 0) ss << "abc def";
            else ss << randInt(1900, 2100) << "x " << randInt(1, 12);
            break;
        case 1: // 年份越界
            if (rand() % 2 == 0) ss << randInt(1800, 1899) << " " << randInt(1, 12);
            else ss << randInt(2101, 3000) << " " << randInt(1, 12);
            break;
        case 2: // 月份越界 (<1)
            ss << randInt(1900, 2100) << " " << randInt(-5, 0);
            break;
        case 3: // 月份越界 (>12)
            ss << randInt(1900, 2100) << " " << randInt(13, 20);
            break;
        case 4: // 非数字+数字混合
            ss << "2025a 5" << endl;
            break;
        case 5: // 只有一个数或缺少
            if (rand() % 2 == 0) ss << randInt(1900, 2100);
            else ss << " " << randInt(1, 12);
            break;
    }
    return ss.str();
}

int main() {
    const string logFile = "gen_calendar.log";
    const string seedFile = "seed.txt";
    const string counterFile = "run_counter.txt";

    // 读取随机种子
    unsigned int seed = time(0);
    ifstream seedIn(seedFile);
    if (seedIn.is_open()) {
        seedIn >> seed;
        seedIn.close();
    }
    srand(seed);

    // 读取运行计数器
    int runCount = 0;
    ifstream counterIn(counterFile);
    if (counterIn.is_open()) {
        counterIn >> runCount;
        counterIn.close();
    }

    // 打开日志文件（追加模式）
    ofstream logOut(logFile, ios::app);
    logOut << "\n========== Run " << (runCount + 1) << " ==========" << endl;
    logOut << "Random Seed Used: " << seed << endl;

    vector<string> errorLines;

    // 添加图一相关非法输入（手动构造几个典型错误）
    errorLines.push_back("1900 13");     // 月份超界
    errorLines.push_back("1899 1");      // 年份太小
    errorLines.push_back("2101 6");      // 年份太大
    errorLines.push_back("abc 5");       // 字符
    errorLines.push_back("2020 x");      // 混合
    errorLines.push_back("2020");        // 缺少月份
    errorLines.push_back("  5");         // 缺少年份

    logOut << "Predefined Error Inputs:" << endl;
    for (const auto& err : errorLines) {
        logOut << "  -> \"" << err << "\"" << endl;
    }

    // 添加随机错误输入（3~6行）
    int numRandomErrors = randInt(3, 6);
    for (int i = 0; i < numRandomErrors; i++) {
        string err = generateErrorLine();
        errorLines.push_back(err);
        logOut << "Random Error Input: \"" << err << "\"" << endl;
    }

    // 确定最后一行（正确数据：年 月）
    pair<int, int> finalYM;
    if (runCount < fig1_valid_ym.size()) {
        finalYM = fig1_valid_ym[runCount];
        logOut << "Final Valid Input (Fig1 Case " << (runCount + 1) << "): "
               << finalYM.first << " " << finalYM.second << endl;
    } else {
        // 之后用随机合法年月
        while (true) {
            int y = randInt(1900, 2100);
            int m = randInt(1, 12);
            // 验证该年月是否有效（总是有效，因为月份1-12，年份1900-2100都合法）
            finalYM = {y, m};
            break;
        }
        logOut << "Final Valid Input (Random): "
               << finalYM.first << " " << finalYM.second << endl;
    }

    // 输出到标准输出（供被测程序读取）
    for (const string& line : errorLines) {
        cout << line << endl;
    }
    cout << finalYM.first << " " << finalYM.second << endl;

    logOut << "========================================" << endl;
    logOut.close();

    // 更新计数器
    ofstream counterOut(counterFile);
    counterOut << (runCount + 1) << endl;
    counterOut.close();

    // 生成下一个随机种子并保存（不输出到stdout）
    unsigned int nextSeed = rand();
    ofstream seedOut(seedFile);
    seedOut << nextSeed << endl;
    seedOut.close();

    return 0;
}