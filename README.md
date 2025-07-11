# 🎤 语音输入助手

一个基于 OpenAI Whisper 的高精度 Windows 语音输入助手，支持全局热键、多种输入方式和大模型优化。

## ✨ 主要特性

- **🎯 高精度识别**: 基于 OpenAI Whisper 模型，支持多种规模模型选择
- **🔥 全局热键**: 支持 F9 等自定义热键，随时随地启动语音识别
- **🚀 大模型优化**: 可选 GPT 优化识别结果，显著提升准确率
- **📝 多种输入方式**: 剪贴板、模拟键盘、Windows API 等多种文本输入方式
- **🎨 现代GUI界面**: 完整的设置界面，支持主题切换和实时预览
- **🔔 系统托盘**: 后台运行，托盘图标显示实时状态
- **🌍 智能应用适配**: 针对 Excel、Word、微信等应用优化
- **🛡️ 完全本地化**: 语音识别完全本地处理，保护隐私
- **📦 便携版发布**: 一键打包，无需 Python 环境即可使用

## 📸 界面预览

- **主界面**: 6个功能标签页，涵盖所有设置选项
- **系统托盘**: 绿色正常、红色录音、灰色错误状态显示
- **状态悬浮窗**: 实时显示识别状态和结果

## 🚀 快速开始

### 方法1：使用便携版（推荐）
1. 下载最新的便携版压缩包
2. 解压到任意目录
3. 运行 `启动语音助手.exe`
4. 按 F9 键开始语音识别

### 方法2：源码运行
```bash
# 1. 克隆项目
git clone https://github.com/Yuhamixili/voice_input_assistant.git
cd voice_input_assistant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动程序
python src/main.py
```

## 🎯 使用方法

### 基本操作
1. **启动程序**: 双击运行或使用命令行
2. **语音识别**: 按 F9 键开始录音，说话完成后自动识别
3. **查看状态**: 观察系统托盘图标变化
4. **设置调整**: 右键托盘图标选择"设置"

### 热键说明
- **F9**: 开始语音识别（默认）
- **F10**: 停止录音
- **F11**: 切换录音状态
- **Ctrl+F12**: 显示设置窗口

### 状态指示
- **绿色图标**: 程序正常运行
- **红色图标**: 正在录音
- **灰色图标**: 程序错误或麦克风不可用

## ⚙️ 配置说明

### 语音识别设置
- **模型选择**: tiny/base/small/medium/large (推荐 medium)
- **语言**: 中文/英文/自动检测
- **录音时长**: 5-30秒可调
- **静音检测**: 自动停止录音

### 大模型优化（可选）
启用后可将识别结果从：
```
我说请说一个脚长的句子,包含着点泡。
```
优化为：
```
我说请说一个较长的句子，包含标点符号。
```

配置方法：
```bash
python setup_api_key.py
```

### 文本输入方式
- **剪贴板**: 复制到剪贴板，手动粘贴（推荐）
- **模拟键盘**: 自动模拟键盘输入
- **Windows API**: 直接插入到活动窗口

## 🔧 优化工具

### 语音识别优化
```bash
python optimize_voice_recognition.py
```
- 测试麦克风设备
- 调整识别参数
- 测试识别准确率

### 热键测试
```bash
python test_hotkey.py
```

### 语音识别测试
```bash
python test_voice.py
```

## 📦 打包发布

### 生成便携版
```bash
# Windows一键打包
打包程序.bat

# 或手动打包
python build_exe.py
```

生成的便携版包含：
- 单文件可执行程序
- 完整配置文件
- 详细使用说明
- 一键启动脚本

## 📋 系统要求

### 最低要求
- Windows 10/11 64位
- 4GB RAM
- 2GB 可用磁盘空间
- 麦克风设备

### 推荐配置
- Windows 11
- 8GB+ RAM
- 5GB+ 可用磁盘空间
- 高质量麦克风

## 🔧 故障排除

### 热键无反应
1. 检查程序是否运行（系统托盘图标）
2. 确认没有其他程序占用F9键
3. 以管理员身份运行程序

### 识别准确率低
1. 升级到更大的模型（medium/large）
2. 启用大模型优化
3. 检查麦克风设置和环境噪音
4. 参考 `提升识别准确率指南.md`

### 程序启动失败
1. 运行 `python fix_startup.py` 自动修复
2. 检查依赖包是否完整安装
3. 查看日志文件：`logs/voice_assistant.log`

## 📁 项目结构

```
voice_input_assistant/
├── src/                    # 源代码
│   ├── core/              # 核心功能
│   │   ├── voice_recognizer.py    # 语音识别
│   │   ├── text_injector.py       # 文本注入
│   │   └── hotkey_manager.py      # 热键管理
│   ├── gui/               # 图形界面
│   │   ├── main_window.py         # 主窗口
│   │   └── tray_icon.py           # 系统托盘
│   ├── utils/             # 工具模块
│   │   └── config_manager.py      # 配置管理
│   └── main.py            # 程序入口
├── config/                # 配置文件
├── logs/                  # 日志文件
├── requirements.txt       # 依赖包
├── build_exe.py          # 打包脚本
├── optimize_voice_recognition.py  # 优化工具
├── setup_api_key.py      # API配置工具
└── 提升识别准确率指南.md  # 使用指南
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/Yuhamixili/voice_input_assistant.git

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_modules.py
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [PyQt5](https://riverbankcomputing.com/software/pyqt/) - GUI框架
- [pynput](https://github.com/moses-palmer/pynput) - 全局热键支持
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) - 音频录制

## 📞 支持

如果遇到问题或有建议，请：
1. 查看 [故障排除](#-故障排除) 部分
2. 运行优化工具进行诊断
3. 提交 [Issue](https://github.com/Yuhamixili/voice_input_assistant/issues)

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！ 