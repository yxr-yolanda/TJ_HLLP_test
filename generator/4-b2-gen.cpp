#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>
#include <sstream>

using namespace std;

// 图一中的合法数据 (作为终止的正确输入)
vector<vector<int>> fig1_valid = {
    {1900, 1, 1},
    {1900, 2, 28},
    {1900, 12, 31},
    {2000, 1, 15},
    {2000, 2, 28},
    {2000, 2, 29},
    {2000, 4, 13},
    {2012, 2, 29},
    {2013, 7, 12},
    {2014, 2, 28},
    {2014, 3, 6},
    {2014, 4, 7},
    {2018, 11, 1},
    {2099, 12, 31}
};

// 图一中的非法数据
vector<vector<int>> fig1_invalid = {
    {1900, 2, 29},
    {2014, 2, 29}
};

bool isLeap(int year) {
    return (year % 400 == 0) || (year % 4 == 0 && year % 100 != 0);
}

int getDays(int year, int month) {
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
        case 0:
            if (rand() % 2 == 0) ss << "abc def ghi";
            else ss << randInt(1900, 2100) << "x " << randInt(1, 12);
            break;
        case 1:
            if (rand() % 2 == 0) ss << randInt(1800, 1899) << " " << randInt(1, 12) << " " << randInt(1, 28);
            else ss << randInt(2101, 3000) << " " << randInt(1, 12) << " " << randInt(1, 28);
            break;
        case 2:
            ss << randInt(1900, 2100) << " " << randInt(-5, 0) << " " << randInt(1, 28);
            break;
        case 3:
            ss << randInt(1900, 2100) << " " << randInt(13, 20) << " " << randInt(1, 28);
            break;
        case 4:
            {
                int y = 1900 + randInt(0, 200);
                while (isLeap(y)) y++;
                ss << y << " 2 29";
            }
            break;
        case 5:
            {
                int months[] = {4, 6, 9, 11};
                int m = months[rand() % 4];
                ss << randInt(1900, 2100) << " " << m << " 31";
            }
            break;
    }
    return ss.str();
}

int main() {
    srand(time(0));
    
    const string logFile = "gen.log";
    const string counterFile = "gen_counter.txt";
    
    // 读取计数器
    int runCount = 0;
    ifstream counterIn(counterFile);
    if (counterIn.is_open()) {
        counterIn >> runCount;
        counterIn.close();
    }
    
    // 打开日志文件
    ofstream logOut(logFile, ios::app);
    logOut << "\n========== Run " << (runCount + 1) << " ==========" << endl;
    
    // 添加图一中的非法数据作为错误输入
    vector<string> errorLines;
    for (auto& date : fig1_invalid) {
        stringstream ss;
        ss << date[0] << " " << date[1] << " " << date[2];
        errorLines.push_back(ss.str());
        logOut << "Error Input (Fig1 Illegal): " << ss.str() << endl;
    }
    
    // 添加随机错误输入
    int numRandomErrors = randInt(5, 10);
    for (int i = 0; i < numRandomErrors; i++) {
        string err = generateErrorLine();
        errorLines.push_back(err);
        logOut << "Error Input (Random): " << err << endl;
    }
    
    // 确定最后一行（正确数据）
    vector<int> finalDate;
    if (runCount < fig1_valid.size()) {
        // 使用前14次的图一数据
        finalDate = fig1_valid[runCount];
        logOut << "Final Valid Input (Fig1 Case " << (runCount + 1) << "): " 
               << finalDate[0] << " " << finalDate[1] << " " << finalDate[2] << endl;
    } else {
        // 14次之后使用随机数据
        while (true) {
            int y = randInt(1900, 2100);
            int m = randInt(1, 12);
            int d = randInt(1, 31);
            if (d <= getDays(y, m)) {
                finalDate = {y, m, d};
                break;
            }
        }
        logOut << "Final Valid Input (Random): " 
               << finalDate[0] << " " << finalDate[1] << " " << finalDate[2] << endl;
    }
    
    // 输出到标准输出
    for (const string& line : errorLines) {
        cout << line << endl;
    }
    cout << finalDate[0] << " " << finalDate[1] << " " << finalDate[2] << endl;
    
    logOut << "========================================" << endl;
    logOut.close();
    
    // 更新计数器
    ofstream counterOut(counterFile);
    counterOut << (runCount + 1) << endl;
    counterOut.close();
    
    return 0;
}