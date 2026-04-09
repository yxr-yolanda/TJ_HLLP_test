@echo off
chcp 65001 >nul
echo 🔧 正在打包对拍工具...

REM 清理旧构建
rmdir /s /q build dist 2>nul

REM 打包（单文件 + 窗口模式）
pyinstaller --onefile --windowed ^
    --name "TJ_HLLP_test" ^
    --icon=icon.ico ^
    main.py

if %errorlevel% equ 0 (
    echo ✅ 打包完成！
    echo 📁 可执行文件: dist\TJ_HLLP_test.exe
) else (
    echo ❌ 打包失败
)

pause