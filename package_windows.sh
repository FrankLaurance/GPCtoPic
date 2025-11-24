#!/bin/bash
# Windows 便携版打包脚本
# 使用方法: bash package_windows.sh

set -e  # 遇到错误立即退出

echo "======================================"
echo "  GPCtoPic Windows 便携版打包工具"
echo "======================================"
echo ""

# 配置变量
APP_NAME="GPCtoPic"
VERSION="1.0"
PYTHON_VERSION="3.11.9"  # 使用稳定版本
PYTHON_EMBED_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip"
OUTPUT_DIR="dist_portable_windows"
PACKAGE_NAME="${APP_NAME}_Windows_Portable_v${VERSION}"

# 清理旧的输出目录
if [ -d "$OUTPUT_DIR" ]; then
    echo "[1/8] 清理旧的构建目录..."
    rm -rf "$OUTPUT_DIR"
fi

# 创建输出目录结构
echo "[2/8] 创建目录结构..."
mkdir -p "$OUTPUT_DIR/$PACKAGE_NAME"
cd "$OUTPUT_DIR/$PACKAGE_NAME"

# 下载 Python 嵌入式版本
echo "[3/8] 下载 Python 嵌入式版本 (${PYTHON_VERSION})..."
if ! curl -L -o python_embed.zip "$PYTHON_EMBED_URL"; then
    echo "❌ 下载失败！请检查网络连接或手动下载："
    echo "   $PYTHON_EMBED_URL"
    exit 1
fi

# 解压 Python
echo "[4/8] 解压 Python..."
unzip -q python_embed.zip -d python
rm python_embed.zip

# 修改 python._pth 文件以启用 site-packages
echo "[5/8] 配置 Python 环境..."
PTH_FILE="python/python${PYTHON_VERSION:0:2}._pth"
if [ -f "$PTH_FILE" ]; then
    # 取消注释 import site
    sed -i.bak 's/#import site/import site/' "$PTH_FILE" 2>/dev/null || \
    sed -i '' 's/#import site/import site/' "$PTH_FILE" 2>/dev/null || \
    echo "注意: 无法自动修改 ._pth 文件，请手动编辑"
    
    # 添加 Lib/site-packages 到路径
    echo "Lib/site-packages" >> "$PTH_FILE"
fi

# 下载 get-pip.py
echo "[6/8] 安装 pip..."
curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
./python/python.exe get-pip.py --no-warn-script-location
rm get-pip.py

# 安装依赖
echo "[7/8] 安装应用依赖..."
./python/python.exe -m pip install --no-warn-script-location \
    streamlit==1.32.0 \
    numpy==1.26.4 \
    pandas==2.2.1 \
    matplotlib==3.8.3 \
    plottable==0.1.5 \
    openpyxl==3.1.2

# 复制应用文件
echo "[8/8] 复制应用文件..."
cd ../..
cp main.py "$OUTPUT_DIR/$PACKAGE_NAME/"
cp ui.py "$OUTPUT_DIR/$PACKAGE_NAME/"
cp cnames.py "$OUTPUT_DIR/$PACKAGE_NAME/"
cp run_main.py "$OUTPUT_DIR/$PACKAGE_NAME/"
cp requirements.txt "$OUTPUT_DIR/$PACKAGE_NAME/"
cp README.md "$OUTPUT_DIR/$PACKAGE_NAME/"
cp LICENSE "$OUTPUT_DIR/$PACKAGE_NAME/" 2>/dev/null || true

# 复制必要的目录
cp -r setting "$OUTPUT_DIR/$PACKAGE_NAME/"
cp -r datapath "$OUTPUT_DIR/$PACKAGE_NAME/"
mkdir -p "$OUTPUT_DIR/$PACKAGE_NAME/GPC_output"
mkdir -p "$OUTPUT_DIR/$PACKAGE_NAME/Mw_output"
mkdir -p "$OUTPUT_DIR/$PACKAGE_NAME/logs"

# 复制图片资源（如果存在）
cp sinopec.jpg "$OUTPUT_DIR/$PACKAGE_NAME/" 2>/dev/null || true

# 创建启动脚本
cat > "$OUTPUT_DIR/$PACKAGE_NAME/启动应用.bat" << 'EOF'
@echo off
chcp 65001 >nul
title GPCtoPic - GPC数据处理工具

echo ====================================
echo   GPCtoPic 启动中...
echo ====================================
echo.

:: 设置环境变量
set PYTHONPATH=%~dp0
set MPLBACKEND=Agg

:: 检查 Python 是否存在
if not exist "%~dp0python\python.exe" (
    echo [错误] 找不到 Python 环境！
    echo 请确保 python 文件夹存在。
    pause
    exit /b 1
)

:: 启动应用
echo [信息] 正在启动 Streamlit 应用...
echo [信息] 应用启动后会自动打开浏览器
echo [信息] 如需停止应用，请关闭此窗口
echo.
echo ====================================
echo.

"%~dp0python\python.exe" -m streamlit run "%~dp0run_main.py" --server.headless=true

:: 如果启动失败
if errorlevel 1 (
    echo.
    echo [错误] 应用启动失败！
    echo 请检查日志文件获取详细信息。
    pause
)
EOF

# 创建命令行启动脚本（用于调试）
cat > "$OUTPUT_DIR/$PACKAGE_NAME/命令行启动.bat" << 'EOF'
@echo off
chcp 65001 >nul

echo ====================================
echo   GPCtoPic 命令行模式
echo ====================================
echo.
echo 你现在可以使用 Python 命令
echo 例如: python run_main.py
echo.

set PYTHONPATH=%~dp0
set PATH=%~dp0python;%~dp0python\Scripts;%PATH%

cmd /k "cd /d %~dp0"
EOF

# 创建卸载说明
cat > "$OUTPUT_DIR/$PACKAGE_NAME/如何卸载.txt" << 'EOF'
GPCtoPic 便携版卸载说明
========================

这是一个便携式应用，未在系统中安装任何内容。

卸载方法：
1. 关闭正在运行的应用（如果有）
2. 直接删除整个文件夹即可

所有数据都存储在此文件夹内：
- datapath/     : 输入数据
- GPC_output/   : GPC 输出结果
- Mw_output/    : 分子量输出结果
- logs/         : 日志文件
- setting/      : 配置文件

如需备份数据，请复制上述文件夹。
EOF

# 创建使用说明
cat > "$OUTPUT_DIR/$PACKAGE_NAME/使用说明.txt" << 'EOF'
GPCtoPic Windows 便携版使用说明
================================

快速开始
--------
1. 双击 "启动应用.bat" 
2. 等待浏览器自动打开（通常是 http://localhost:8501）
3. 开始使用应用

文件夹说明
----------
- datapath/     : 放置 .rst 数据文件
- GPC_output/   : GPC 处理结果输出位置
- Mw_output/    : 分子量数据输出位置
- setting/      : 配置文件存储位置
- logs/         : 应用日志文件
- python/       : Python 运行环境（请勿删除）

常见问题
--------
Q: 应用无法启动？
A: 1. 检查是否有杀毒软件阻止
   2. 尝试右键"以管理员身份运行"
   3. 查看 logs/ 文件夹中的日志

Q: 浏览器没有自动打开？
A: 手动打开浏览器访问 http://localhost:8501

Q: 如何停止应用？
A: 关闭命令行窗口即可

Q: 可以移动到其他位置吗？
A: 可以，整个文件夹可以移动到任何位置

技术支持
--------
GitHub: https://github.com/FrankLaurance/GPCtoPic
问题反馈: 请在 GitHub 提交 Issue

版本信息
--------
应用版本: 1.0
Python 版本: 3.11.9
EOF

# 创建 README
cat > "$OUTPUT_DIR/$PACKAGE_NAME/README_Windows.md" << 'EOF'
# GPCtoPic Windows 便携版

## 简介
这是 GPCtoPic 的 Windows 便携版本，无需安装 Python 环境，解压即可使用。

## 系统要求
- Windows 10/11 (64位)
- 至少 500MB 可用磁盘空间
- 网络连接（首次启动时）

## 快速开始

### 方法一：双击启动（推荐）
1. 双击 `启动应用.bat`
2. 等待浏览器自动打开
3. 开始使用

### 方法二：命令行启动
1. 双击 `命令行启动.bat`
2. 输入命令：`python -m streamlit run run_main.py`

## 文件结构
```
GPCtoPic_Windows_Portable/
├── 启动应用.bat          # 一键启动脚本
├── 命令行启动.bat        # 命令行模式
├── 使用说明.txt          # 详细使用说明
├── python/              # Python 运行环境
├── main.py              # 主程序
├── ui.py                # 用户界面
├── datapath/            # 数据输入目录
├── GPC_output/          # GPC 输出目录
├── Mw_output/           # 分子量输出目录
├── setting/             # 配置文件目录
└── logs/                # 日志文件目录
```

## 使用流程
1. 将 .rst 数据文件放入 `datapath/` 文件夹
2. 启动应用
3. 在网页界面中选择文件并处理
4. 结果会保存在 `GPC_output/` 和 `Mw_output/` 文件夹

## 注意事项
- 首次启动可能需要较长时间（加载依赖）
- 请勿删除 `python/` 文件夹
- 杀毒软件可能误报，请添加信任
- 关闭命令行窗口会停止应用

## 卸载
直接删除整个文件夹即可，无需其他操作。

## 技术支持
- GitHub: https://github.com/FrankLaurance/GPCtoPic
- 问题反馈: 提交 GitHub Issue

## 许可证
请查看 LICENSE 文件
EOF

# 压缩打包
echo ""
echo "======================================"
echo "  打包完成！"
echo "======================================"
echo ""
echo "输出目录: $OUTPUT_DIR/$PACKAGE_NAME"
echo ""
echo "下一步操作："
echo "1. 测试: cd $OUTPUT_DIR/$PACKAGE_NAME && ./启动应用.bat"
echo "2. 压缩: zip -r ${PACKAGE_NAME}.zip $OUTPUT_DIR/$PACKAGE_NAME"
echo "3. 分发: 将 ${PACKAGE_NAME}.zip 发给用户"
echo ""
echo "提示: 在 Windows 上测试启动脚本"
echo ""

# 可选：自动创建 zip 包
read -p "是否立即创建 ZIP 压缩包? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd ..
    echo "正在压缩..."
    zip -r -q "${PACKAGE_NAME}.zip" "$PACKAGE_NAME"
    echo "✅ 压缩包已创建: $OUTPUT_DIR/${PACKAGE_NAME}.zip"
    
    # 显示文件大小
    SIZE=$(du -h "${PACKAGE_NAME}.zip" | cut -f1)
    echo "📦 文件大小: $SIZE"
fi

echo ""
echo "✅ 全部完成！"
