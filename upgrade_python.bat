@echo off
echo ========================================
echo Python 3.8.10 升级助手
echo ========================================
echo.

echo 当前Python版本:
python --version
echo.

echo 请按照以下步骤操作:
echo.
echo 1. 访问 https://www.python.org/downloads/release/python-3810/
echo 2. 下载 Windows 64位安装包 (python-3.8.10-amd64.exe)
echo 3. 运行安装程序，确保勾选 "Add Python 3.8 to PATH"
echo 4. 安装完成后，关闭此窗口并重新打开
echo 5. 运行以下命令验证:
echo    python --version
echo    python -m pip --version
echo.

echo 安装完成后，运行以下命令重新安装项目依赖:
echo    python -m venv venv
echo    venv\Scripts\activate.bat
echo    pip install -r requirements.txt
echo.

pause
