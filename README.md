# GPCtoPic - GPC数据可视化工具

一个用于处理和可视化GPC(凝胶渗透色谱)数据的Python工具，可以生成柱状图、分子量分布曲线和数据表格。

## ✨ 功能特点

- 📊 自动读取和处理GPC数据文件
- 📈 生成精美的柱状图和分子量分布曲线
- 📋 创建格式化的数据表格
- 🎨 支持自定义颜色、字体大小等样式
- 💾 批量导出高质量图片(PNG/PDF)
- 🖥️ 基于Streamlit的Web界面，操作简单直观
- 📦 支持打包为独立可执行文件

## 🚀 快速开始

### 方式一：直接运行Python脚本

#### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/FrankLaurance/GPCtoPic.git
cd GPCtoPic

# 创建虚拟环境（推荐）
python -m venv myenv

# 激活虚拟环境
# macOS/Linux:
source myenv/bin/activate
# Windows:
myenv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

#### 2. 运行程序

```bash
streamlit run main.py
```

程序将自动在浏览器中打开，默认地址为 `http://localhost:8501`

### 方式二：使用打包后的可执行文件

下载已打包的可执行文件（从Releases页面），双击运行即可，无需安装Python环境。

## 📖 使用说明

### 1. 准备数据文件

将GPC数据文件放在指定目录中

数据文件应包含以下列：
- 分子量相关数据 (Mn, Mw, Mz等)
- 分布数据 (PDI等)

### 2. 配置参数

在Web界面的侧边栏中，您可以配置：

**基本设置：**
- 数据目录路径
- 保存文件选项
- 生成图片选项

**样式设置：**
- 柱状图颜色
- 分子量曲线颜色
- 柱状图宽度
- 曲线宽度
- 坐标轴宽度

**字体设置：**
- 标题字体大小
- 坐标轴字体大小

**图表选项：**
- 是否绘制柱状图
- 是否绘制分子量曲线
- 是否生成数据表格
- 是否使用透明背景

### 3. 生成图表

1. 设置好参数后，点击"开始处理"按钮
2. 程序将自动处理数据目录中的所有文件
3. 生成的图片将保存在 `datapath` 目录下
4. 处理完成后可在界面中预览结果

### 4. 查看结果

- 点击"打开数据文件夹"按钮可直接打开保存图片的目录
- 所有生成的图片都会在界面中展示预览

## 🔧 配置文件

程序使用 `setting/defaultSetting.ini` 作为默认配置文件，包含以下参数：

```ini
[DEFAULT]
DataDir = datapath
SaveFile = True
BarWidth = 1.2
LineWidth = 1.0
AxisWidth = 1.0
TitleFontSize = 20
AxisFontSize = 14
TransparentBack = True
SavePicture = True
DisplayPicture = False
BarColor = #002FA7
MwColor = #FF6A07
DrawBar = True
DrawMw = True
DrawTable = True
```

您可以根据需要修改配置文件，或在Web界面中直接调整参数。

## 📦 打包为可执行文件

### 自动打包（推荐）

使用提供的脚本自动完成打包：

**macOS/Linux:**
```bash
chmod +x build.sh
./build.sh
```

**Windows:**
```powershell
.\build.ps1
```

### 手动打包

#### 1. 安装PyInstaller

```bash
pip install pyinstaller
```

**Windows:**
从 [UPX官网](https://upx.github.io/) 下载并添加到PATH

#### 2. 执行打包

```bash
pyinstaller GPCtoPic.spec
```

打包完成后，可执行文件将位于 `dist/GPCtoPic` 目录中。

详细打包说明请参考 [BUILD_README.md](BUILD_README.md)

## 📋 依赖包

- streamlit >= 1.20.0
- numpy >= 1.20.0
- pandas >= 1.3.0
- matplotlib >= 3.5.0
- plottable >= 0.1.0
- openpyxl >= 3.0.0

## 🖥️ 系统要求

- Python 3.8+
- macOS / Windows / Linux

## 📝 项目结构

```
GPCtoPic/
├── main.py                 # 主程序文件
├── run_main.py            # 运行启动脚本
├── cnames.py              # 中文名称映射
├── requirements.txt       # Python依赖
├── GPCtoPic.spec         # PyInstaller配置文件
├── build.sh              # macOS/Linux打包脚本
├── build.ps1             # Windows打包脚本
├── BUILD_README.md       # 打包详细说明
├── main.ico              # 程序图标
├── sinopec.jpg           # 页面图标
├── setting/              # 配置文件目录
│   └── defaultSetting.ini
└── datapath/             # 数据文件目录（默认）
```

## 🐛 故障排除

### 问题1：程序无法启动
- 确认已安装所有依赖包：`pip install -r requirements.txt`
- 检查Python版本是否为3.8或更高

### 问题2：找不到数据文件
- 确认数据文件路径设置正确
- 检查数据文件格式是否支持

### 问题3：图片无法保存
- 确认有数据输出目录的写入权限
- 检查磁盘空间是否充足

### 问题4：打包后文件过大
- 确认已按照BUILD_README.md中的优化步骤操作
- 安装UPX进行压缩

## 📄 许可证

本项目采用 MIT 许可证。

## 👤 作者

FrankLaurance

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📮 联系方式

如有问题或建议，请通过GitHub Issues联系。
