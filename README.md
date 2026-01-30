# 🧭 VoyaAI

> 基于 AI 的实时数据集成旅游行程生成器

VoyaAI 是一款智能旅游规划助手，利用大语言模型和模型上下文协议 (MCP) 创建个性化的旅游行程。它整合了来自多个源的信息，生成全面且美观的 HTML 格式旅游指南。

## ✨ 特性

- 📱 **小红书集成** - 获取热门旅游贴士和评论
- 🌤️ **实时天气** - 获取目的地城市的实时天气预报
- 🗺️ **路线规划** - 使用高德地图 API 生成优化路线
- 🎨 **精美输出** - 生成响应式设计的可打印 HTML 旅游指南
- 🤖 **兼容 OpenAI** - 支持任何兼容 OpenAI 的 API（如 GPT, Claude, Gemini 等）

## 🚀 快速开始

### 前置要求

- Python 3.11+
- 一个兼容 OpenAI 的 API 终端（直接 API 或 OneAPI, LiteLLM, New API 等中转服务）
- (可选) 高德地图 API Key（用于路线规划）
- (可选) 小红书 MCP 服务

### 安装

```bash
# 克隆仓库
git clone https://github.com/MorseWayne/VoyaAI.git
cd VoyaAI

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 用户: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 配置

编辑 `.env` 文件：

```env
# LLM 配置 (兼容 OpenAI 的 API)
LLM_BASE_URL=http://127.0.0.1:8045/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-3-flash

# 可选: MCP 服务
AMAP_MCP_URL=https://mcp.amap.com/sse?key=your_amap_key
WEATHER_MCP_URL=http://localhost:8083/sse
```

**支持的 API 提供商：**

| 提供商 | Base URL 示例 |
|----------|-----------------|
| OpenAI 直连 | `https://api.openai.com/v1` |
| Azure OpenAI | `https://your-resource.openai.azure.com/openai/deployments/your-deployment` |
| OneAPI/New API | `http://127.0.0.1:3000/v1` |
| LiteLLM | `http://127.0.0.1:4000/v1` |
| Ollama | `http://127.0.0.1:11434/v1` |

### 运行服务器

```bash
python main.py
```

服务器将运行在 `http://localhost:8182`

## 📖 API 使用

### 生成旅游计划 (POST)

```bash
curl -X POST "http://localhost:8182/travel/plan" \
     -H "Content-Type: application/json" \
     -d '{"content": "请帮我规划一份日本大阪5天的旅游攻略，预算5000-6000元"}'
```

### 简单查询 (GET)

```bash
curl "http://localhost:8182/travel/chat?content=日本大阪5天游攻略"
```

### 查看生成的 HTML

```bash
curl "http://localhost:8182/travel/html"
```

或者直接在浏览器访问 `http://localhost:8182/travel/html`。

### 测试接口

```bash
curl "http://localhost:8182/test?content=Hello"
```

### 查看服务状态

```bash
curl "http://localhost:8182/status"
```

## 🧪 测试

项目提供了独立的测试脚本，用于验证各个 MCP 服务是否正常工作：

```bash
# 测试 LLM 连接
python tests/test_llm.py

# 测试小红书 MCP
python tests/test_xhs_mcp.py

# 测试天气 MCP
python tests/test_weather_mcp.py

# 测试高德地图 MCP
python tests/test_amap_mcp.py

# 运行所有测试
python tests/test_all.py

# 只测试特定服务
python tests/test_all.py --llm
python tests/test_all.py --xhs
```

## 📁 项目结构

```
VoyaAI/
├── main.py              # 应用程序入口
├── config/
│   └── settings.py      # 配置管理
├── api/
│   └── routes.py        # FastAPI 路由
├── services/
│   ├── llm_factory.py   # OpenAI 客户端及 Agent 实现
│   └── travel_service.py # 核心业务逻辑
├── mcp/
│   └── clients.py       # MCP 工具集成
├── prompts/
│   ├── travel_guide.txt # 旅游规划提示词
│   └── html_template.txt # HTML 生成提示词
├── tests/               # 测试脚本
│   ├── test_llm.py      # LLM 连接测试
│   ├── test_xhs_mcp.py  # 小红书 MCP 测试
│   ├── test_weather_mcp.py # 天气 MCP 测试
│   ├── test_amap_mcp.py # 高德地图 MCP 测试
│   └── test_all.py      # 综合测试
└── output/              # 生成的文件
```

## 🔧 技术栈

| 组件 | 技术 |
|-----------|------------|
| 框架 | FastAPI |
| LLM SDK | OpenAI Python SDK |
| LLM | 任何兼容 OpenAI 的 API |
| 协议 | MCP (Model Context Protocol) |
| Language | Python 3.11+ |

## 🏗️ 架构图

```
┌─────────────────┐     ┌─────────────────┐
│   FastAPI       │────▶│  TravelService  │
│   (routes.py)   │     │                 │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │ Agent (Tools) │         │ Agent (HTML)  │
           │ - 小红书集成    │         │ - 不使用工具    │
           │ - 实时天气      │         │ - 转换为 HTML  │
           │ - 路线规划      │         └───────────────┘
           │ - POI 信息      │
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │ OpenAI Client │
           │ (代理或直连)     │
           └───────────────┘
```

## 📝 请求示例

```text
你好，我需要你为我策划一份详尽的日本旅游攻略。
以下是我的具体需求：
1. 核心旅行参数：
   - 预算范围：5000-6000
   - 行程时长：5天～6天
   - 期望出行时间：6月20日-6月25日
   - 出发城市：广州
   - 出行人群：一对夫妇
   - 偏好城市：大阪
2. 行程风格与偏好：
   - 行程节奏：轻松舒适
   - 必去景点：环球影城，购物
```

## 🤝 参与贡献

欢迎提交 PR 参与贡献！

## 📄 许可证

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 特别感谢

- Java 版本的原始实现 [Cooosin](https://github.com/Cooosin)
- 提供 Python SDK 的 [OpenAI](https://github.com/openai/openai-python)
- 工具集成协议 [MCP](https://modelcontextprotocol.io/)
