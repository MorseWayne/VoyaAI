# AigoHotel MCP 工具说明

本文档描述通过 AigoHotel MCP（Model Context Protocol）服务提供的工具，用于酒店搜索与元数据获取。文档内容由实际 MCP 工具定义抓取整理而成。

## 配置

在 `.env` 中配置：

| 变量 | 说明 |
|------|------|
| `AIGOHOTEL_MCP_URL` | MCP 服务地址，例如 `https://mcp.aigohotel.com/mcp` |
| `AIGOHOTEL_MCP_TOKEN` | Bearer 令牌，用于 `Authorization: Bearer <token>` |

请求头会自动带上：

- `Authorization: Bearer <AIGOHOTEL_MCP_TOKEN>`
- `Content-Type: application/json`

## 工具列表

| 工具名 | 说明 |
|--------|------|
| [getHotelSearchTags](#gethotelsearchtags) | 获取酒店搜索元数据（标签列表等），供 Agent 缓存与意图解析 |
| [searchHotels](#searchhotels) | 按地点、日期、星级、人数等条件搜索全球酒店 |

---

## getHotelSearchTags

获取酒店搜索元数据（AI Cache），包含可用的标签列表（以当前启用数据为准）。

**用途**：供 AI Agent 缓存使用，帮助 Agent 在本地解析用户意图，然后传入结构化的 `hotelTags` 参数调用 `searchHotels`。

**优势**：跳过服务端 AI 解析，减少一次模型调用耗时，整体响应更稳定（实际耗时仍取决于实时查价等环节，通常为秒级）。

**使用建议**：

1. 启动时调用一次并缓存返回的标签列表
2. 用户搜索酒店时，根据缓存的元数据解析用户需求
3. 将解析结果通过 `hotelTags` 参数传入 `searchHotels`

**返回内容**：

- `tags`：所有可用的酒店标签（按分类组织）
- `usageGuide`：使用指南和示例

### 参数

无入参。

---

## searchHotels

按城市、景点或酒店名称等地点条件，以及日期、入住天数、星级、人数、距离和设施等多维条件筛选，返回符合条件的酒店列表。

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `place` | string | 是 | 地点名称，尽可能详细并带上国家/城市，例如：北京、上海浦东国际机场、迪士尼乐园等 |
| `placeType` | string | 是 | 地点类型。支持：城市、机场、景点、火车站、地铁站、酒店、区/县、详细地址 |
| `originQuery` | string | 是 | 用户的提问语句；未填写时默认取 `place` |
| `countryCode` | string | 否 | 国家三字码，例如：CHN |
| `checkIn` | string | 否 | 入住日期，如：2025-10-01；未填写时默认次日 |
| `stayNights` | integer | 否 | 入住天数；未填写时默认 1 天 |
| `starRatings` | array of number | 否 | 酒店星级（0.0–5.0，步长 0.5），默认 [0.0, 5.0]。例如 [4.5, 5.0]、[0.0, 2.0] |
| `adultCount` | integer | 否 | 每间房成人数量；默认 2 |
| `distanceInMeter` | integer | 否 | 直线距离（米）；当地点为 POI 时生效，生效时默认 5000 |
| `size` | integer | 否 | 返回酒店数量；默认 10，最大 20 |
| `withHotelAmenities` | boolean | 否 | 是否包含酒店设施 |
| `language` | string | 否 | 语言环境，如 zh_CN、en_US；默认 zh_CN |
| `queryParsing` | boolean | 否 | 是否对用户提问做需求倾向分析；默认 true |
| `hotelTags` | object | 否 | 酒店筛选标签；建议先调用 `getHotelSearchTags` 获取可用标签。结构见下表 |

### hotelTags 对象结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `preferredTags` | string[] | 用户偏好的酒店标签列表（从 getHotelSearchTags 返回的标签中选择） |
| `excludedTags` | string[] | 用户不想要的酒店标签列表（排除条件），格式同 preferredTags |
| `requiredTags` | string[] | 用户必须满足的酒店标签列表（强约束），格式同 preferredTags |
| `preferredBrands` | string[] | 用户偏好的酒店品牌名称。常见：希尔顿、万豪、洲际、香格里拉、凯悦、雅高、温德姆、精选国际、华住、锦江、首旅如家、亚朵、维也纳等 |
| `maxPricePerNight` | number | 每晚最高预算，单位：人民币 |
| `minRoomSize` | integer | 最低房间面积要求，单位：平方米 |

### 可用标签分类（preferredTags / excludedTags / requiredTags）

标签需从 `getHotelSearchTags` 返回的列表中选择，以下为参考分类：

- **品牌与评分**：国际连锁品牌、当地热门品牌、单体酒店  
- **特色卖点**：临近商场、赌场酒店、乐园酒店、提供会议设施、商务中心、宴会厅、无障碍停车位、无障碍通道、提供无障碍客房、酒店主题特色、仅限成人入住、提供SPA服务  
- **核心设施**：公共温泉、私人海滩、公共海滩、洗衣服务、室内恒温泳池、户外泳池、健身房、免费WiFi、免费停车场  
- **亲子家庭**：儿童乐园、儿童泳池、儿童玩乐设施、可提供婴儿床或围栏、提供家庭房  
- **服务细节**：宠物友好、中文标识、中文服务  
- **服务与餐饮**：供应中式早餐、24小时前台、客房点餐、私人管家、快速办理入住/退房  
- **交通与支付**：机场接送班车、自行车租赁、支持支付宝/微信、支持银联卡  
- **景观与房型**：客房备有拖鞋、客房备有热水壶、客房备有吹风机、提供联通房、提供别墅房型、提供电竞主题房、智能客房、提供可吸烟房、提供大床房、提供双床房、提供特色床型、提供三人间、提供四人间、部分客房带有海景/城景/山景、部分客房无窗、部分客房带有花园景  
- **酒店类型**：性价比酒店、品质酒店、亲子酒店、度假酒店、华人友好酒店、运动友好酒店、商务酒店、无障碍友好酒店、机场酒店  

---

## 在项目中的使用

- MCP 客户端：`mcp_services/clients.py` 中的 `MCPService` 支持自定义 headers，`MCPClientManager.from_settings()` 会按配置注册 `aigohotel` 服务。
- 测试脚本：`uv run python tests/test_aigohotel_mcp.py` 可验证配置、连接及工具发现与调用。

---

*文档根据 AigoHotel MCP 当前工具定义整理，若服务端有更新请以实际 `list_tools` 返回为准。*
