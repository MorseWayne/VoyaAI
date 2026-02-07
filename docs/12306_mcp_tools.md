# 12306 MCP 工具说明

本文档描述通过 12306 MCP（Model Context Protocol）服务提供的工具，用于中国铁路12306火车票查询。文档内容由实际 MCP 工具定义整理而成。

## 配置

在 `.env` 中配置：

| 变量 | 说明 |
|------|------|
| `12306_MCP_URL` | MCP 服务地址，例如 `https://mcp.12306.com/mcp` |
| `12306_MCP_TOKEN` | Bearer 令牌，用于 `Authorization: Bearer <token>` |

请求头会自动带上：

- `Authorization: Bearer <12306_MCP_TOKEN>`
- `Content-Type: application/json`

## 工具列表

| 工具名 | 说明 |
|--------|------|
| [get-current-date](#get-current-date) | 获取当前日期（用于处理相对日期） |
| [get-stations-code-in-city](#get-stations-code-in-city) | 通过中文城市名查询该城市所有火车站的名称及其对应的station_code |
| [get-station-code-of-citys](#get-station-code-of-citys) | 通过中文城市名查询代表该城市的station_code |
| [get-station-code-by-names](#get-station-code-by-names) | 通过具体的中文车站名查询其station_code和车站名 |
| [get-station-by-telecode](#get-station-by-telecode) | 通过车站的station_telecode查询车站的详细信息 |
| [get-tickets](#get-tickets) | 查询12306余票信息 |
| [get-interline-tickets](#get-interline-tickets) | 查询12306中转余票信息 |
| [get-train-route-stations](#get-train-route-stations) | 查询特定列车车次的详细经停信息 |

---

## get-current-date

获取当前日期，以上海时区（Asia/Shanghai, UTC+8）为准，返回格式为 "yyyy-MM-dd"。主要用于解析用户提到的相对日期（如"明天"、"下周三"），提供准确的日期输入。

**用途**：在处理用户查询中涉及相对日期时使用，确保日期计算准确。

**返回内容**：
- 当前日期字符串，格式：yyyy-MM-dd

### 参数

无入参。

---

## get-stations-code-in-city

通过中文城市名查询该城市 **所有** 火车站的名称及其对应的 `station_code`，结果是一个包含多个车站信息的列表。

**用途**：当用户提供城市名时，获取该城市的所有火车站信息，便于后续查询。

**返回内容**：
- 车站列表，每个车站包含：
  - `station_code`：车站编码（如：ZHQ）
  - `station_name`：车站名称（如：珠海）

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `city` | string | 是 | 中文城市名称，例如："北京"、"上海" |

---

## get-station-code-of-citys

通过中文城市名查询代表该城市的 `station_code`。此接口主要用于在用户提供**城市名**作为出发地或到达地时，为接口准备 `station_code` 参数。

**用途**：快速获取城市的主要火车站编码，用于票务查询。

**返回内容**：
- 城市对应的车站编码信息

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `citys` | string | 是 | 要查询的城市，比如"北京"。若要查询多个城市，请用\|分割，比如"北京\|上海"。 |

---

## get-station-code-by-names

通过具体的中文车站名查询其 `station_code` 和车站名。此接口主要用于在用户提供**具体车站名**作为出发地或到达地时，为接口准备 `station_code` 参数。

**用途**：通过具体车站名称获取对应的编码，用于精确的票务查询。

**返回内容**：
- 车站编码和名称信息

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `stationNames` | string | 是 | 具体的中文车站名称，例如："北京南"、"上海虹桥"。若要查询多个站点，请用\|分割，比如"北京南\|上海虹桥"。 |

---

## get-station-by-telecode

通过车站的 `station_telecode` 查询车站的详细信息，包括名称、拼音、所属城市等。此接口主要用于在已知 `telecode` 的情况下获取更完整的车站数据，或用于特殊查询及调试目的。

**用途**：获取车站的详细信息，常用于调试或需要完整车站信息时。

**返回内容**：
- 车站的详细信息（名称、拼音、城市等）

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `stationTelecode` | string | 是 | 车站的 `station_telecode` (3位字母编码) |

---

## get-tickets

查询12306余票信息。

**用途**：查询两站之间的直达列车余票信息，是最常用的查询功能。

**使用建议**：
1. 查询前务必先获取出发地和到达地的 `station_code`
2. 支持多种筛选条件来缩小查询范围
3. 可以设置时间范围和排序方式

**返回内容**：
- 车次列表，包含：
  - 车次信息（车次号、出发到达站、时间、历时）
  - 余票信息（各席别余票数量和价格）
  - 支持文本、CSV、JSON格式输出

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `date` | string | 是 | 查询日期，格式为 "yyyy-MM-dd"。如果用户提供的是相对日期，请先调用 `get-current-date` 获取当前日期并计算目标日期。 |
| `fromStation` | string | 是 | 出发地的 `station_code`。必须是通过其他接口查询得到的编码，严禁直接使用中文地名。 |
| `toStation` | string | 是 | 到达地的 `station_code`。必须是通过其他接口查询得到的编码，严禁直接使用中文地名。 |
| `trainFilterFlags` | string | 否 | 车次筛选条件，默认为空，即不筛选。支持多个标志同时筛选。例如用户说"高铁票"，则应使用 "G"。可选标志：[G(高铁/城际),D(动车),Z(直达特快),T(特快),K(快速),O(其他),F(复兴号),S(智能动车组)] |
| `earliestStartTime` | number | 否 | 最早出发时间（0-24），默认为0。 |
| `latestStartTime` | number | 否 | 最迟出发时间（0-24），默认为24。 |
| `sortFlag` | string | 否 | 排序方式，默认为空，即不排序。仅支持单一标识。可选标志：[startTime(出发时间从早到晚), arriveTime(抵达时间从早到晚), duration(历时从短到长)] |
| `sortReverse` | boolean | 否 | 是否逆向排序结果，默认为false。仅在设置了sortFlag时生效。 |
| `limitedNum` | number | 否 | 返回的余票数量限制，默认为0，即不限制。 |
| `format` | string | 否 | 返回结果格式，默认为text，建议使用text与csv。可选标志：[text, csv, json] |

---

## get-interline-tickets

查询12306中转余票信息。尚且只支持查询前十条。

**用途**：查询需要中转的列车方案，当直达车次不足或用户需要中转时使用。

**使用建议**：
1. 中转查询较为复杂，建议设置合适的筛选条件
2. 当前仅返回前10条结果

**返回内容**：
- 中转方案列表，包含：
  - 第一程和第二程的车次信息
  - 中转站信息
  - 总历时和换乘时间
  - 余票信息

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `date` | string | 是 | 查询日期，格式为 "yyyy-MM-dd"。如果用户提供的是相对日期，请先调用 `get-current-date` 获取当前日期并计算目标日期。 |
| `fromStation` | string | 是 | 出发地的 `station_code`。必须是通过其他接口查询得到的编码，严禁直接使用中文地名。 |
| `toStation` | string | 是 | 到达地的 `station_code`。必须是通过其他接口查询得到的编码，严禁直接使用中文地名。 |
| `middleStation` | string | 否 | 中转地的 `station_code`，可选。必须是通过其他接口查询得到的编码，严禁直接使用中文地名。 |
| `showWZ` | boolean | 否 | 是否显示无座车，默认不显示无座车。 |
| `trainFilterFlags` | string | 否 | 车次筛选条件，默认为空。从以下标志中选取多个条件组合[G(高铁/城际),D(动车),Z(直达特快),T(特快),K(快速),O(其他),F(复兴号),S(智能动车组)] |
| `earliestStartTime` | number | 否 | 最早出发时间（0-24），默认为0。 |
| `latestStartTime` | number | 否 | 最迟出发时间（0-24），默认为24。 |
| `sortFlag` | string | 否 | 排序方式，默认为空，即不排序。仅支持单一标识。可选标志：[startTime(出发时间从早到晚), arriveTime(抵达时间从早到晚), duration(历时从短到长)] |
| `sortReverse` | boolean | 否 | 是否逆向排序结果，默认为false。仅在设置了sortFlag时生效。 |
| `limitedNum` | number | 否 | 返回的中转余票数量限制，默认为10。 |
| `format` | string | 否 | 返回结果格式，默认为text，建议使用text。可选标志：[text, json] |

---

## get-train-route-stations

查询特定列车车次在指定区间内的途径车站、到站时间、出发时间及停留时间等详细经停信息。当用户询问某趟具体列车的经停站时使用此接口。

**用途**：获取列车详细的经停信息，包括每个途径站的到发时间和停留时间。

**使用建议**：
1. 当用户询问具体车次的经停站时使用
2. 需要提供准确的车次号和出发日期

**返回内容**：
- 列车经停站列表，包含：
  - 途径车站名称
  - 到站时间
  - 出发时间
  - 停留时间

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `trainCode` | string | 是 | 要查询的车次 `train_code`，例如" G1033 "。 |
| `departDate` | string | 是 | 列车出发的日期 (格式: yyyy-MM-dd)。如果用户提供的是相对日期，请先调用 `get-current-date` 解析。 |
| `format` | string | 否 | 返回结果格式，默认为text，建议使用text。可选标志：[text, json] |

---

## 在项目中的使用

- MCP 客户端：`mcp_services/clients.py` 中的 `MCPService` 支持自定义 headers，`MCPClientManager.from_settings()` 会按配置注册 `12306` 服务。
- 测试脚本：可以创建测试脚本来验证配置、连接及工具发现与调用。

---

*文档根据 12306 MCP 当前工具定义整理，若服务端有更新请以实际 `list_tools` 返回为准。*