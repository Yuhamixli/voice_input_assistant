# 语音输入助手

一个基于Whisper的高精度Windows语音输入助手，支持大模型优化，适用于Excel、Word、聊天软件等各种场景。

## 🎯 项目特点

- **高精度识别**: 基于OpenAI Whisper模型，中文识别准确率高
- **多种输入方式**: 支持剪贴板、模拟键盘、Windows API等多种文本输入方式
- **智能应用适配**: 针对Excel、Word、微信等应用程序进行专门优化
- **全局热键**: 支持自定义热键，操作便捷
- **大模型优化**: 可选择性使用GPT等大模型优化识别结果
- **系统托盘**: 后台运行，不占用桌面空间
- **完全本地化**: 语音识别完全在本地进行，保护隐私
- **开源免费**: 基于MIT许可证开源

## 📋 系统要求

- Windows 10/11
- Python 3.8+
- 麦克风设备
- 至少4GB RAM（推荐8GB以上）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-username/voice_input_assistant.git
cd voice_input_assistant

# 安装依赖包
pip install -r requirements.txt
```

### 1.5. 配置环境变量（可选）

如果要使用大模型优化功能：

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑.env文件，填入你的API密钥
# 例如：OPENAI_API_KEY=your_api_key_here
```

### 2. 启动程序

```bash
# 方式1：静默启动（推荐，无需用户交互）
python start_silent.py

# 方式2：交互式启动
python start.py

# 方式3：使用批处理文件
静默启动.bat         # 静默启动
启动语音助手.bat      # 交互式启动

# 方式4：直接运行主程序
python src/main.py
```

首次启动会自动下载Whisper模型，请耐心等待。

### 3. 基本使用

1. 程序启动后会在系统托盘显示麦克风图标
2. 按下 `F9` 键开始语音识别
3. 清晰地说出要输入的内容
4. 程序会自动识别并输入到当前光标位置

## 🔧 功能配置

### 语音识别设置

- **模型选择**: 支持tiny、base、small、medium、large等不同大小的模型
- **语言设置**: 支持中文、英文、自动检测
- **录音参数**: 可调整录音时长、采样率、降噪等参数

### 热键配置

默认热键：
- `F9`: 开始语音识别
- `F10`: 停止语音识别
- `F11`: 切换语音识别状态
- `Ctrl+F12`: 显示设置窗口

所有热键都可以在设置中自定义。

### 文本输入方式

1. **剪贴板方式**（推荐）: 通过剪贴板粘贴文本
2. **模拟键盘**: 模拟键盘输入
3. **Windows API**: 使用系统API直接发送文本

### 应用程序优化

针对以下应用程序进行了专门优化：
- Microsoft Excel
- Microsoft Word
- 微信 (WeChat)
- QQ
- 记事本
- 浏览器

## 🤖 大模型优化

支持使用OpenAI GPT等大模型对识别结果进行优化：

1. 在设置中启用"大模型优化"
2. 输入OpenAI API Key
3. 选择合适的模型（如gpt-3.5-turbo）
4. 自定义优化提示词

大模型优化可以：
- 纠正语音识别错误
- 添加合适的标点符号
- 规范化表达方式
- 提升文本质量

## 📁 项目结构

```
voice_input_assistant/
├── src/                    # 源代码目录
│   ├── core/              # 核心模块
│   │   ├── voice_recognizer.py    # 语音识别器
│   │   ├── text_injector.py       # 文本注入器
│   │   └── hotkey_manager.py      # 热键管理器
│   ├── gui/               # 图形界面
│   │   ├── main_window.py         # 主窗口
│   │   └── tray_icon.py           # 系统托盘
│   ├── utils/             # 工具模块
│   │   └── config_manager.py      # 配置管理器
│   └── main.py            # 主程序入口
├── config/                # 配置文件目录
│   └── config.example.ini # 配置示例文件
├── logs/                  # 日志文件目录
├── requirements.txt       # 依赖包列表
├── start.py               # 交互式启动脚本
├── start_silent.py        # 静默启动脚本
├── test_modules.py        # 模块测试脚本
├── fix_startup.py         # 启动问题修复脚本
├── build_exe.py           # 打包脚本
├── 启动语音助手.bat        # Windows启动批处理
├── 静默启动.bat            # Windows静默启动批处理
├── 打包程序.bat           # Windows打包批处理
├── env.example            # 环境变量示例文件
├── 使用说明.md            # 详细使用说明
├── check_release.py       # 发布前检查脚本
├── .gitignore            # Git忽略文件
├── LICENSE               # 许可证文件
└── README.md             # 项目说明
```

## 🎛️ 高级设置

### 配置文件

配置文件位于 `config/config.ini`，包含以下主要配置：

```ini
[voice_recognition]
model = base                # Whisper模型
language = zh              # 语言
duration = 5               # 录音时长

[hotkeys]
start_recording = f9       # 开始录音热键
stop_recording = f10       # 停止录音热键

[text_input]
method = clipboard         # 输入方式
smart_mode = true          # 智能模式

[llm_optimization]
enabled = false            # 启用大模型优化
model = gpt-3.5-turbo     # 大模型名称
api_key =                 # API密钥
```

### 日志记录

程序会自动生成日志文件，位于 `logs/` 目录：
- 自动轮转，单个文件最大10MB
- 保留最近7天的日志
- 包含详细的操作记录和错误信息

### 性能优化

1. **模型选择**: 根据需要选择合适的Whisper模型
   - tiny: 速度快，精度较低
   - base: 平衡速度和精度（推荐）
   - large: 精度高，速度慢

2. **音频设置**: 调整采样率和音频参数
3. **智能模式**: 根据应用程序自动调整输入方式

## 📦 打包发布

### 打包为exe文件

```bash
# 安装打包依赖
pip install pyinstaller pillow

# 执行打包
python build_exe.py
```

打包完成后会生成：
- `dist/语音输入助手.exe` - 单文件exe
- `dist/语音输入助手_便携版/` - 便携版文件夹
- `dist/语音输入助手_便携版.zip` - 便携版压缩包

### 便携版特点

- **免安装**：解压即用，无需安装Python环境
- **完整功能**：包含所有核心功能
- **配置文件**：包含配置示例和使用说明
- **环境变量**：支持.env文件配置API密钥
- **一键启动**：提供批处理启动脚本

### 分发给其他用户

1. 将 `语音输入助手_便携版.zip` 发送给用户
2. 用户解压后双击 `启动语音助手.bat` 即可使用
3. 如需大模型优化，复制 `env.example` 为 `.env` 并填入API密钥

### 环境变量配置

支持通过环境变量配置常用设置，优先级：**环境变量 > 配置文件 > 默认值**

```bash
# 复制示例文件
cp env.example .env

# 编辑.env文件
OPENAI_API_KEY=your_openai_api_key_here
WHISPER_MODEL=base
ENABLE_LLM_OPTIMIZATION=true
```

主要环境变量：
- `OPENAI_API_KEY`: OpenAI API密钥
- `WHISPER_MODEL`: Whisper模型大小（tiny/base/small/medium/large）
- `ENABLE_LLM_OPTIMIZATION`: 是否启用大模型优化
- `CUSTOM_HOTKEY`: 自定义热键
- `UI_THEME`: 界面主题（light/dark）

## 🔍 故障排除

### 快速修复

如果遇到启动问题，请按顺序尝试以下方法：

```bash
# 1. 运行修复脚本（推荐）
python fix_startup.py

# 2. 使用静默启动
python start_silent.py

# 3. 测试模块
python test_modules.py

# 4. 清理并重新安装
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 常见问题

1. **启动失败："input(): lost sys.stdin"**
   - 使用静默启动：`python start_silent.py` 或 `静默启动.bat`
   - 这是因为在某些环境下标准输入不可用
   - 静默启动版本会自动处理这个问题
   - 或者运行修复脚本：`python fix_startup.py`

2. **麦克风无法识别**
   - 检查麦克风是否正确连接
   - 确认Windows音频设备设置
   - 在程序设置中测试音频设备

3. **识别准确率低**
   - 确保在安静环境中使用
   - 调整麦克风距离和音量
   - 说话时保持正常语速
   - 尝试使用更大的Whisper模型

4. **文本输入失败**
   - 尝试不同的输入方式
   - 检查目标应用程序是否支持
   - 确认光标位置正确

5. **热键冲突**
   - 在设置中修改热键
   - 避免与其他程序热键冲突

### 调试模式

启用调试模式可以获取更多信息：
1. 编辑配置文件，设置 `debug_mode = true`
2. 重启程序
3. 查看详细的日志信息

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目基于MIT许可证开源，详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [pynput](https://github.com/moses-palmer/pynput) - 键盘监听
- [pyautogui](https://github.com/asweigart/pyautogui) - 自动化操作

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/voice_input_assistant/issues)
- 发送邮件至: your-email@example.com

---

**注意**: 本项目仅供学习和研究使用，使用过程中请遵守相关法律法规。 