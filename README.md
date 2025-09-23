# Lab Asset Manager - 核心后端模块

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/opencv-4.5+-green.svg)](https://opencv.org/)

## 🎯 模块概述

Lab Asset Manager 核心后端模块是一个集成了多种现代技术的智能化实验室设备管理平台。该系统通过计算机视觉、人工智能、二维码技术和Web API，为实验室提供了一套完整的资产管理解决方案。

### ✨ 核心功能

- 🤖 **AI图像分析**: 支持OpenAI GPT-4V、Anthropic Claude、Ollama等多种LLM提供商
- 📷 **智能相机集成**: 实时图像捕获、预览和设备识别
- 🔬 **eLabFTW集成**: 与实验室信息管理系统无缝对接，支持完整的CRUD操作
- 🏷️ **二维码管理**: 自动生成和管理资产二维码标签
- 🌐 **Web API服务**: 基于Flask的RESTful API接口
- ⚙️ **统一配置管理**: 前后端配置同步，支持实时设置更新
- 🔄 **实时通信**: 基于Socket.IO的实时数据传输

### 🏗️ 技术特点

- **模块化架构**: 清晰的模块划分，易于维护和扩展
- **统一配置管理**: 消除硬编码，提高系统可配置性
- **跨平台支持**: 支持Windows、macOS、Linux、Raspberry Pi
- **RESTful API**: 标准化的API接口设计
- **异步处理**: 支持长时间运行的AI分析任务
- **错误处理**: 完善的异常处理和日志记录

## 系统架构

### 后端架构 (Python)
```
lab_asset_manager/
├── config/              # 统一配置管理
├── camera/              # 相机功能模块
├── elabftw/            # ELabFTW集成模块
├── llm/                # AI分析模块
├── qrcode_module/      # 二维码生成模块
├── ui/                 # 用户界面模块
└── web/                # Web服务模块
```

### 前端架构 (Vue.js)
```
web/client/
├── src/
│   ├── components/     # Vue组件
│   ├── views/         # 页面视图
│   ├── services/      # API服务
│   ├── store/         # 状态管理
│   └── router/        # 路由配置
└── dist/              # 构建输出
```

## 🚀 安装与配置

### 📋 环境要求

- **Python**: 3.8+ (推荐 3.9+)
- **Node.js**: 14+ (用于前端开发)
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+), Raspberry Pi OS
- **硬件**: USB摄像头（可选），至少2GB RAM

### ⚡ 快速安装

```bash
# 1. 进入项目目录
cd lab_asset_manager

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装Python依赖
pip install -r requirements.txt

# 4. 配置系统
cp config.example.json config.json
# 编辑 config.json 文件配置API密钥等参数

# 5. 启动Web API服务器
python web_api.py
```

### 🔧 详细配置

#### 配置文件结构

编辑 `config.json` 文件，配置以下参数：

```json
{
  "llm": {
    "api_key": "your_openai_api_key",
    "model": "gpt-4-vision-preview",
    "temperature": 0.1,
    "max_tokens": 1000,
    "ollama_url": "http://localhost:11434"
  },
  "elabftw": {
    "api_url": "https://your-elabftw.com/api/v2",
    "api_key": "your_elabftw_api_key",
    "default_category": "1",
    "team_id": "1",
    "hide_token": true,
    "verify_ssl": true
  },
  "camera": {
    "device_id": 0,
    "resolution": [1920, 1080],
    "fps": 30,
    "auto_start": false
  },
  "ui": {
    "theme": "light",
    "language": "zh-CN"
  },
  "storage": {
    "images_dir": "images",
    "qrcodes_dir": "qrcodes"
  }
}
```

#### 🔑 API密钥配置

1. **OpenAI API**:
   ```bash
   # 在 https://platform.openai.com/ 获取API密钥
   # 支持 GPT-4 Vision 模型进行图像分析
   ```

2. **Anthropic Claude**:
   ```bash
   # 在 https://console.anthropic.com/ 获取API密钥
   # 支持 Claude-3 Vision 模型
   ```

3. **Ollama本地模型**:
   ```bash
   # 安装Ollama: https://ollama.ai/
   ollama pull llava:latest  # 本地视觉模型
   ```

4. **eLabFTW集成**:
   ```bash
   # 在您的eLabFTW实例中生成API密钥
   # 路径: 用户设置 -> API密钥
   ```

## 使用方法

### 启动系统

1. **启动后端服务**
```bash
python main.py
```

2. **启动Web服务**
```bash
cd web
npm start
```

3. **访问Web界面**
打开浏览器访问：`http://localhost:3000`

### 主要功能使用

#### 1. 相机管理
- 查看相机状态：`python camera/camera_status.py`
- 捕获图像：`python camera/capture_image.py`
- 相机设置：通过Web界面或配置文件

#### 2. ELabFTW集成
- 获取实验模板：`python elabftw/get_templates.py`
- 创建实验项目：`python elabftw/create_item.py`
- 更新实验数据：`python elabftw/update_item.py`

#### 3. AI图像分析
- 分析图像：`python llm/analyze_image.py <image_path>`
- 配置AI模型：编辑配置文件中的llm部分

#### 4. 二维码管理
- 生成二维码：`python export_qrcode.py`
- 批量生成：`python export_qrcode_direct.py`
- 简单生成：`python export_qrcode_simple.py`

### Web界面功能

- **仪表板**：系统状态总览
- **资产管理**：查看和管理实验室资产
- **相机控制**：实时相机预览和控制
- **二维码生成**：在线生成和管理二维码
- **设置**：系统配置和参数调整

## 项目结构

```
lab_asset_manager/
├── __init__.py                    # 项目包初始化
├── README.md                      # 项目说明文档
├── requirements.txt               # Python依赖列表
├── 技术知识点总结.md              # 技术文档
├── config/                        # 配置管理模块
│   ├── __init__.py
│   ├── config.example.json        # 配置文件模板
│   ├── config.json               # 实际配置文件
│   ├── paths.py                  # 路径管理
│   └── settings.py               # 配置管理类
├── camera/                        # 相机功能模块
│   ├── __init__.py
│   ├── camera_manager.py         # 相机管理器
│   ├── camera_settings.py        # 相机设置
│   ├── camera_status.py          # 相机状态检查
│   ├── capture_image.py          # 图像捕获
│   ├── get_settings.py           # 设置获取
│   └── stream_camera.py          # 相机流处理
├── elabftw/                       # ELabFTW集成模块
│   ├── __init__.py
│   ├── create_item.py            # 创建实验项目
│   ├── elab_manager.py           # ELabFTW管理器
│   ├── get_item.py               # 获取实验项目
│   ├── get_items.py              # 获取项目列表
│   ├── get_settings.py           # 获取设置
│   ├── get_templates.py          # 获取模板
│   └── update_item.py            # 更新实验项目
├── llm/                          # AI分析模块
│   ├── __init__.py
│   ├── analyze_image.py          # 图像分析
│   ├── get_settings.py           # LLM设置获取
│   ├── llm_manager.py            # LLM管理器
│   └── llm_settings.py           # LLM设置
├── qrcode_module/                # 二维码模块
│   ├── __init__.py
│   └── qrcode_generator.py       # 二维码生成器
├── ui/                           # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py            # 主窗口
│   └── ui_manager.py             # UI管理器
├── web/                          # Web服务模块
│   ├── README.md                 # Web模块说明
│   ├── package.json              # Node.js依赖
│   ├── package-lock.json         # 依赖锁定文件
│   ├── config.json               # Web配置
│   ├── client/                   # 前端应用
│   │   ├── package.json
│   │   ├── package-lock.json
│   │   ├── dist/                 # 构建输出
│   │   └── src/                  # 源代码
│   │       ├── App.vue           # 主应用组件
│   │       ├── main.js           # 应用入口
│   │       ├── components/       # Vue组件
│   │       │   ├── AssetManagementComponent.vue
│   │       │   ├── CameraComponent.vue
│   │       │   ├── ElabFTWComponent.vue
│   │       │   ├── ElabIntegrationComponent.vue
│   │       │   ├── LLMAnalysisComponent.vue
│   │       │   ├── QRCodeComponent.vue
│   │       │   ├── ResponsiveLayout.vue
│   │       │   └── SettingsComponent.vue
│   │       ├── views/            # 页面视图
│   │       │   ├── AssetsView.vue
│   │       │   ├── CameraView.vue
│   │       │   ├── Dashboard.vue
│   │       │   ├── HomeView.vue
│   │       │   ├── QRCodesView.vue
│   │       │   └── SettingsView.vue
│   │       ├── router/           # 路由配置
│   │       │   └── index.js
│   │       ├── services/         # API服务
│   │       │   └── api.js
│   │       └── store/            # 状态管理
│   │           └── index.js
│   └── server/                   # 后端服务
│       ├── index.js              # 服务器入口
│       └── routes/               # API路由
│           ├── camera.js
│           ├── elab.js
│           ├── llm.js
│           └── qrcode.js
├── images/                       # 图像存储目录
├── qrcodes/                      # 二维码存储目录
├── utils/                        # 工具模块
├── elab/                         # ELab桥接模块
├── qrcode/                       # QR码桥接模块
├── test_function/                # 测试功能
├── main.py                       # 主程序入口
├── export_qrcode.py              # 二维码导出
├── export_qrcode_direct.py       # 直接二维码导出
├── export_qrcode_simple.py       # 简单二维码导出
├── fix_qrcode.py                 # 二维码修复
├── test_import.py                # 导入测试
├── test_qrcode.py                # 二维码测试
├── test_qrcode.png               # 测试二维码
├── start_web.sh                  # Web启动脚本
└── lab_asset_manager.log         # 系统日志
```

## 📚 API文档

### 🌐 Web API服务器

启动API服务器：
```bash
python web_api.py
# 服务器运行在 http://localhost:5001
```

### 📷 相机API

```bash
# 获取相机状态
GET /api/camera/status
Response: {"status": "ready", "device_id": 0, "resolution": [1920, 1080]}

# 捕获图像
POST /api/camera/capture
Response: {"success": true, "image_path": "images/asset_20240101_120000.jpg"}

# 获取相机设置
GET /api/camera/settings
Response: {"device_id": 0, "resolution": [1920, 1080], "fps": 30}

# 更新相机设置
POST /api/camera/settings
Body: {"device_id": 0, "resolution": [1280, 720], "fps": 24}
```

### 🤖 LLM分析API

```bash
# 分析图像
POST /api/llm/analyze
Body: {"image_path": "images/sample.jpg", "prompt": "分析这个实验设备"}
Response: {
  "success": true,
  "analysis": "这是一个离心机设备...",
  "timestamp": "2024-01-01T12:00:00Z"
}

# 获取LLM设置
GET /api/llm/settings
Response: {
  "api_key_configured": true,
  "model": "gpt-4-vision-preview",
  "temperature": 0.1,
  "max_tokens": 1000,
  "ollama_url": "http://localhost:11434"
}

# 更新LLM设置
POST /api/llm/settings
Body: {
  "api_key": "new_api_key",
  "model": "gpt-4-vision-preview",
  "temperature": 0.2
}
```

### 🔬 eLabFTW集成API

```bash
# 获取eLabFTW设置
GET /api/elab/settings
Response: {
  "api_url": "https://your-elabftw.com/api/v2",
  "default_category": "1",
  "team_id": "1",
  "hide_token": true,
  "verify_ssl": true
}

# 更新eLabFTW设置
POST /api/elab/settings
Body: {
  "api_url": "https://new-elabftw.com/api/v2",
  "api_key": "new_api_key",
  "verify_ssl": false
}

# 获取实验模板
GET /api/elab/templates
Response: [
  {"id": 1, "name": "设备登记模板", "category": "资产管理"},
  {"id": 2, "name": "维护记录模板", "category": "维护"}
]

# 创建实验项目
POST /api/elab/items
Body: {
  "title": "新设备登记",
  "body": "设备详细信息...",
  "category_id": 1
}

# 获取实验项目
GET /api/elab/items/:id
Response: {
  "id": 123,
  "title": "设备登记",
  "body": "设备信息...",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 🏷️ 二维码API

```bash
# 生成二维码
POST /api/qrcode/generate
Body: {
  "data": "https://elabftw.com/database.php?mode=view&id=123",
  "filename": "asset_123.png"
}
Response: {
  "success": true,
  "qrcode_path": "qrcodes/asset_123.png"
}

# 获取二维码列表
GET /api/qrcode/list
Response: [
  {"filename": "asset_123.png", "created_at": "2024-01-01T12:00:00Z"},
  {"filename": "asset_124.png", "created_at": "2024-01-01T12:05:00Z"}
]

# 删除二维码
DELETE /api/qrcode/:filename
Response: {"success": true, "message": "QR code deleted"}
```

### 🔧 系统状态API

```bash
# 获取系统状态
GET /api/system/status
Response: {
  "camera": {"status": "ready", "device_count": 1},
  "llm": {"configured": true, "model": "gpt-4-vision-preview"},
  "elabftw": {"connected": true, "api_url": "https://elabftw.com"},
  "storage": {"images_count": 45, "qrcodes_count": 23}
}

# 获取系统日志
GET /api/system/logs?lines=100
Response: {
  "logs": ["2024-01-01 12:00:00 - INFO - System started", "..."]
}
```

## 🛠️ 开发指南

### 📋 代码规范

- **Python**: 遵循PEP 8代码规范，使用type hints
- **JavaScript**: 使用ESLint和Prettier进行代码格式化
- **文档**: 统一的docstring和注释规范
- **架构**: 模块化设计，单一职责原则
- **版本控制**: 使用语义化版本号

### 🏗️ 开发环境设置

```bash
# 1. 设置开发环境
python -m venv venv
source venv/bin/activate

# 2. 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8  # 开发工具

# 3. 设置pre-commit hooks
pip install pre-commit
pre-commit install

# 4. 启动开发服务器
python web_api.py --debug
```

### 🧪 测试

```bash
# Python单元测试
python -m pytest tests/ -v

# 代码覆盖率
python -m pytest --cov=. --cov-report=html

# API测试
python -m pytest tests/test_api.py

# 集成测试
python test_function/test_integration.py
```

### 📁 模块开发指南

#### 添加新的LLM提供商
```python
# 在 llm/llm_manager.py 中添加新的提供商
class NewLLMProvider:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
    
    def analyze_image(self, image_path, prompt):
        # 实现图像分析逻辑
        pass
```

#### 添加新的API端点
```python
# 在 web_api.py 中添加新的路由
@app.route('/api/new_feature', methods=['POST'])
def new_feature():
    try:
        # 处理请求逻辑
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### 🔄 部署指南

#### 开发部署
```bash
# 启动开发服务器
python web_api.py --host=0.0.0.0 --port=5001 --debug
```

#### 生产部署
```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 web_api:app

# 使用systemd服务
sudo cp lab-asset-manager.service /etc/systemd/system/
sudo systemctl enable lab-asset-manager
sudo systemctl start lab-asset-manager
```

#### 树莓派部署
```bash
# 优化配置
export OPENCV_LOG_LEVEL=ERROR
export PYTHONUNBUFFERED=1

# 启动服务
python web_api.py --host=0.0.0.0 --port=5001
```

## 🔍 故障排除

### 🚨 常见问题解决

| 问题类型 | 症状 | 解决方案 |
|---------|------|----------|
| 🚫 **API服务无法启动** | `Address already in use` | `lsof -i :5001` 查看端口占用，`kill -9 <PID>` 终止进程 |
| 📷 **相机连接失败** | `Camera not found` | 检查设备ID配置，验证USB连接，更新驱动程序 |
| 🤖 **LLM分析超时** | `Request timeout` | 检查网络连接，增加timeout设置，验证API密钥 |
| 🔬 **eLabFTW连接错误** | `SSL verification failed` | 设置`verify_ssl: false`或更新证书 |
| ⚙️ **配置不同步** | 设置不生效 | 检查config.json权限，重启服务，验证JSON格式 |
| 💾 **存储空间不足** | `No space left` | 清理images/qrcodes目录，检查磁盘空间 |

### 📋 调试工具

```bash
# 1. 查看系统日志
tail -f lab_asset_manager.log

# 2. 查看Web API日志
tail -f web_api.log

# 3. 检查系统状态
curl -X GET http://localhost:5001/api/system/status

# 4. 测试相机功能
python camera/camera_status.py

# 5. 测试LLM连接
python llm/llm_settings.py --test

# 6. 验证eLabFTW连接
python elabftw/get_settings.py --verify
```

### 🔧 性能优化

```bash
# 1. 图像处理优化
# 在config.json中调整分辨率
"camera": {"resolution": [1280, 720]}  # 降低分辨率提高性能

# 2. LLM响应优化
"llm": {"max_tokens": 500}  # 减少token数量

# 3. 内存使用优化
export OPENCV_VIDEOIO_PRIORITY_MSMF=0  # Windows优化
export OPENCV_VIDEOIO_PRIORITY_V4L2=0  # Linux优化
```

### 📊 监控和维护

```bash
# 系统资源监控
htop  # 查看CPU和内存使用
df -h  # 查看磁盘空间
netstat -tlnp | grep 5001  # 查看端口状态

# 日志轮转设置
# 在 /etc/logrotate.d/lab-asset-manager 中配置
/path/to/lab_asset_manager/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## 更新日志

### v1.0.0 (当前版本)
- 初始版本发布
- 完整的模块化架构
- 统一配置管理系统
- Web界面集成
- 多功能API支持

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues：[GitHub Issues](项目地址/issues)
- 邮箱：your-email@example.com

## 致谢

感谢所有为本项目做出贡献的开发者和用户。

---

**注意**：本文档会随着项目的发展持续更新，请定期查看最新版本。