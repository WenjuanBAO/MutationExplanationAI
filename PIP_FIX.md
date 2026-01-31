# pip命令问题解决方案

## 问题
在PowerShell中运行 `pip install fastapi` 时出现错误：
```
pip : 无法将"pip"项识别为 cmdlet、函数、脚本文件或可运行程序的名称
```

## 解决方案

### 方案1：使用 `python -m pip`（推荐，立即可用）

直接使用Python模块方式调用pip：

```powershell
# 安装fastapi
python -m pip install fastapi

# 安装所有依赖
python -m pip install -r requirements.txt

# 升级pip
python -m pip install --upgrade pip
```

### 方案2：将pip添加到PATH环境变量

1. 找到Python安装目录和Scripts目录：
   ```powershell
   python -c "import sys; print(sys.executable)"
   python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"
   ```

2. 添加到PATH：
   - 打开"系统属性" > "环境变量"
   - 在"用户变量"或"系统变量"中找到"Path"
   - 添加Python的Scripts目录（例如：`C:\Users\你的用户名\AppData\Local\Programs\Python\Python314\Scripts`）
   - 重启PowerShell

### 方案3：创建pip别名（PowerShell）

在PowerShell中创建别名：

```powershell
# 临时别名（当前会话有效）
Set-Alias pip "python -m pip"

# 永久别名（添加到PowerShell配置文件）
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content -Path $PROFILE -Value "Set-Alias pip 'python -m pip'"
```

## 当前状态

- ✅ Python版本：3.14.2（满足项目要求Python 3.8+）
- ✅ pip可用：通过 `python -m pip` 可以使用
- ❌ pip命令：不在PATH中

## 快速安装项目依赖

```powershell
# 进入项目目录
cd MutationExplanationAI

# 使用python -m pip安装依赖
python -m pip install -r requirements.txt
```

## 关于Python版本

当前Python版本是3.14.2，比要求的3.8.10更新。如果项目依赖都兼容，可以继续使用。如果需要降级到3.8.10，请参考 `PYTHON_UPGRADE_GUIDE.md`。
