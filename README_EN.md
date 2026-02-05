# 🧭 VoyaAI

> AI-powered travel itinerary generator with real-time data integration

VoyaAI is an intelligent travel planning assistant that leverages Large Language Models and the Model Context Protocol (MCP) to create personalized travel itineraries. It aggregates information from multiple sources to generate comprehensive, ready-to-use travel plans presented as beautifully formatted HTML pages.

## ✨ Features

- 📱 **Xiaohongshu Integration** - Fetches trending travel tips and reviews
- 🌤️ **Real-time Weather** - Retrieves weather forecasts for destination cities
- 🗺️ **Route Planning** - Generates optimized routes using Amap (Gaode Maps)
- 🎨 **Beautiful Output** - Produces print-ready HTML travel guides with responsive design
- 🤖 **OpenAI Compatible** - Works with any OpenAI-compatible API (GPT, Claude, Gemini, etc.)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- An OpenAI-compatible API endpoint (direct API or proxy service like OneAPI, LiteLLM, New API)
- (Optional) Amap API key for route planning
- (Optional) Xiaohongshu MCP service

### Installation

```bash
# Clone the repository
git clone https://github.com/MorseWayne/VoyaAI.git
cd VoyaAI

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file with your settings:

```env
# LLM Configuration (OpenAI Compatible API)
LLM_BASE_URL=http://127.0.0.1:8045/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-3-flash

# Optional: MCP Services
AMAP_MCP_URL=https://mcp.amap.com/sse?key=your_amap_key
WEATHER_MCP_URL=http://localhost:8083/sse
```

**Supported API Providers:**

| Provider | Base URL Example |
|----------|-----------------|
| OpenAI Direct | `https://api.openai.com/v1` |
| Azure OpenAI | `https://your-resource.openai.azure.com/openai/deployments/your-deployment` |
| OneAPI/New API | `http://127.0.0.1:3000/v1` |
| LiteLLM | `http://127.0.0.1:4000/v1` |
| Ollama | `http://127.0.0.1:11434/v1` |

### Run the Server

```bash
uv run python main.py
```

The server will start at `http://localhost:8182`

## 📖 API Usage

### Generate Travel Plan (POST)

```bash
curl -X POST "http://localhost:8182/travel/plan" \
     -H "Content-Type: application/json" \
     -d '{"content": "请帮我规划一份日本大阪5天的旅游攻略，预算5000-6000元"}'
```

### Simple Query (GET)

```bash
curl "http://localhost:8182/travel/chat?content=日本大阪5天游攻略"
```

### View Generated HTML

```bash
curl "http://localhost:8182/travel/html"
```

Or open `http://localhost:8182/travel/html` in your browser.

### Test Endpoint

```bash
curl "http://localhost:8182/test?content=Hello"
```

## 📁 Project Structure

```
VoyaAI/
├── main.py              # Application entry point
├── config/
│   └── settings.py      # Configuration management
├── api/
│   └── routes.py        # FastAPI endpoints
├── services/
│   ├── llm_factory.py   # OpenAI client & Agent implementation
│   └── travel_service.py # Core business logic
├── mcp/
│   └── clients.py       # MCP tool integrations
├── prompts/
│   ├── travel_guide.txt # Travel planning prompt
│   └── html_template.txt # HTML generation prompt
└── output/              # Generated files
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| LLM SDK | OpenAI Python SDK |
| LLM | Any OpenAI-compatible API |
| Protocol | MCP (Model Context Protocol) |
| Language | Python 3.11+ |

## 🏗️ Architecture

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
           │ - Xiaohongshu │         │ - No tools    │
           │ - Weather     │         │ - Convert to  │
           │ - Route       │         │   HTML        │
           │ - POI         │         │               │
           └───────┬───────┘         └───────────────┘
                   │
                   ▼
           ┌───────────────┐
           │ OpenAI Client │
           │ (Proxy/Direct)│
           └───────────────┘
```

## 📝 Example Request

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Java implementation by [Cooosin](https://github.com/Cooosin)
- [OpenAI](https://github.com/openai/openai-python) for the Python SDK
- [MCP](https://modelcontextprotocol.io/) for the tool integration protocol
