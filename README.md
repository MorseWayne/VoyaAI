# 🧭 VoyaAI

> AI-powered travel itinerary generator with real-time data integration

VoyaAI is an intelligent travel planning assistant that leverages Large Language Models and the Model Context Protocol (MCP) to create personalized travel itineraries. It aggregates information from multiple sources to generate comprehensive, ready-to-use travel plans presented as beautifully formatted HTML pages.

## ✨ Features

- 📱 **Xiaohongshu Integration** - Fetches trending travel tips and reviews
- 🌤️ **Real-time Weather** - Retrieves weather forecasts for destination cities
- 🗺️ **Route Planning** - Generates optimized routes using Amap (Gaode Maps)
- 🎨 **Beautiful Output** - Produces print-ready HTML travel guides with responsive design
- 🤖 **Multi-LLM Support** - Works with Claude, GPT-4, or Gemini

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- An API key for your preferred LLM (Anthropic, OpenAI, or Google)
- (Optional) Amap API key for route planning
- (Optional) Xiaohongshu MCP service

### Installation

```bash
# Clone the repository
git clone https://github.com/MorseWayne/VoyaAI.git
cd VoyaAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file with your settings:

```env
# Choose your LLM provider: anthropic, openai, or google
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key

# Optional: MCP Services
AMAP_MCP_URL=https://mcp.amap.com/sse?key=your_amap_key
```

### Run the Server

```bash
python main.py
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

## 📁 Project Structure

```
VoyaAI/
├── main.py              # Application entry point
├── config/
│   └── settings.py      # Configuration management
├── api/
│   └── routes.py        # FastAPI endpoints
├── services/
│   ├── llm_factory.py   # LLM initialization
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
| AI Framework | LangChain |
| LLM | Claude / GPT-4 / Gemini |
| Protocol | MCP (Model Context Protocol) |
| Language | Python 3.11+ |

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
- [LangChain](https://github.com/langchain-ai/langchain) for the AI framework
- [MCP](https://modelcontextprotocol.io/) for the tool integration protocol
