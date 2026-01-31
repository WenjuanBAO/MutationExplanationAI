# Python 3.8.10 升级指南

## 当前状态
- **当前版本**: Python 3.7.9
- **目标版本**: Python 3.8.10

## 方法1：使用官方安装包（推荐）

### 步骤1：下载Python 3.8.10

访问Python官网下载页面：
- **Windows 64位**: https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
- **Windows 32位**: https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe

或者访问：https://www.python.org/downloads/release/python-3810/

### 步骤2：安装Python 3.8.10

1. 运行下载的安装程序
2. **重要**: 勾选 "Add Python 3.8 to PATH"（将Python添加到PATH环境变量）
3. 选择 "Install Now" 或 "Customize installation"
4. 如果选择自定义安装，确保勾选：
   - pip
   - tcl/tk and IDLE
   - Python test suite
   - py launcher
   - for all users (可选)

### 步骤3：验证安装

打开新的命令提示符或PowerShell窗口，运行：

```bash
python --version
```

应该显示：`Python 3.8.10`

```bash
python -m pip --version
```

验证pip是否正常工作。

### 步骤4：更新项目依赖

安装完Python 3.8.10后，需要重新安装项目依赖：

```bash
# 进入项目目录
cd MutationExplanationAI

# 创建新的虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

## 方法2：使用pyenv-win（管理多个Python版本）

如果您需要管理多个Python版本，可以使用pyenv-win：

### 安装pyenv-win

```powershell
# 使用PowerShell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

### 使用pyenv安装Python 3.8.10

```bash
pyenv install 3.8.10
pyenv local 3.8.10
```

## 方法3：使用Anaconda/Miniconda

如果您使用Anaconda或Miniconda：

```bash
# 创建新环境
conda create -n mutation_ai python=3.8.10

# 激活环境
conda activate mutation_ai

# 安装依赖
pip install -r requirements.txt
```

## 注意事项

### 1. 环境变量配置

安装后，确保Python在PATH中：
- 打开"系统属性" > "环境变量"
- 检查PATH中是否包含Python安装路径（如：`C:\Python38` 和 `C:\Python38\Scripts`）

### 2. 虚拟环境

强烈建议使用虚拟环境来隔离项目依赖：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1  # PowerShell
# 或
venv\Scripts\activate.bat    # CMD
```

### 3. 重新安装依赖

升级Python后，需要重新安装所有依赖包：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 验证兼容性

项目要求Python 3.8+，3.8.10完全满足要求。主要依赖包都支持Python 3.8。

## 验证安装成功

运行以下命令验证：

```bash
# 检查Python版本
python --version
# 应该显示: Python 3.8.10

# 检查pip
pip --version

# 测试项目
python -c "import sys; print(f'Python {sys.version}')"
```

## 常见问题

### Q: 安装后仍然显示旧版本？
A: 
1. 关闭所有命令提示符/PowerShell窗口
2. 重新打开新的窗口
3. 检查PATH环境变量顺序，确保新版本路径在前

### Q: 如何同时保留多个Python版本？
A: 使用pyenv-win或为不同版本创建不同的虚拟环境。

### Q: 安装时提示"需要管理员权限"？
A: 右键安装程序，选择"以管理员身份运行"。

## 安装后测试

安装完成后，运行项目测试：

```bash
# 进入项目目录
cd MutationExplanationAI

# 创建并激活虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 运行配置测试
python test_config.py
```
