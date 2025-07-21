# 测试文件目录

本目录包含语音输入助手的各种测试脚本。

## 📁 测试文件说明

### 功能测试
- **test_voice.py** - 语音识别功能测试
- **test_hotkey.py** - 热键功能测试
- **test_keyboard.py** - 键盘输入功能测试
- **test_modules.py** - 模块依赖测试

## 🚀 运行测试

从项目根目录运行：

```bash
# 测试语音识别
python tests/test_voice.py

# 测试热键功能
python tests/test_hotkey.py

# 测试键盘输入
python tests/test_keyboard.py

# 测试模块依赖
python tests/test_modules.py
```

## 💡 测试说明

- 所有测试脚本都可以独立运行
- 测试前请确保已安装所有依赖包
- 语音测试需要连接麦克风设备
- 热键测试需要管理员权限（某些系统）

## 🔧 添加新测试

在添加新测试时，请遵循以下命名规范：
- 文件名：`test_<功能名>.py`
- 包含必要的文档说明
- 独立运行，不依赖其他测试文件 