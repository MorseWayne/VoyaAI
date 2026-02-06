# 高德地图 Web 服务 API 完整能力与参数手册

本文档汇总整理了高德地图核心 Web 服务 API 的详细能力、接口地址及完整的调用参数说明。

---

## 1. 路径规划 2.0 (V5 接口) - 推荐使用

提供更强大的路线规划能力，支持多策略、限行规避、室内算路等。

### 1.1 驾车路径规划

**服务地址**: `https://restapi.amap.com/v5/direction/driving` (GET/POST)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 请求服务权限标识 | 用户在高德地图官网申请的 Web 服务 API 类型 Key | 是 | 无 |
| **origin** | 起点经纬度 | 经度在前，纬度在后，用","分割，小数点后不超过6位 | 是 | 无 |
| **destination** | 目的地经纬度 | 经度在前，纬度在后，用","分割，小数点后不超过6位 | 是 | 无 |
| destination_type | 终点 POI 类别 | 当用户知道终点类别时建议填充 | 否 | 无 |
| origin_id | 起点 POI ID | 建议填充，可提升路线规划准确性 | 否 | 无 |
| destination_id | 目的地 POI ID | 建议填充，可提升路线规划准确性 | 否 | 无 |
| **strategy** | 驾车算路策略 | 0:速度, 1:费用, 2:常规, 32:默认(推荐), 33:躲避拥堵, 34:高速优先, 35:不走高速, 36:少收费, 37:大路优先, 38:速度最快, 39-45:组合策略 | 否 | 32 |
| waypoints | 途经点 | 坐标串，分号分隔，最大支持16个途经点 | 否 | 无 |
| avoidpolygons | 避让区域 | 最多32个区域，每个区域最多16顶点，用"\|"分隔区域 | 否 | 无 |
| plate | 车牌号码 | 如 "京AHA322"，用于判断限行 | 否 | 无 |
| cartype | 车辆类型 | 0:普通燃油车, 1:纯电动车, 2:插电式混动汽车 | 否 | 0 |
| ferry | 是否使用轮渡 | 0:使用渡轮, 1:不使用渡轮 | 否 | 0 |
| show_fields | 返回结果控制 | 筛选可选字段(如 cost, tmcs, navi, cities, polyline)，逗号分隔 | 否 | 空 |
| sig | 数字签名 | 签名校验 | 否 | 无 |
| output | 返回结果格式 | 可选值：JSON | 否 | json |
| callback | 回调函数 | 仅在 output=JSON 时有效 | 否 | 无 |

### 1.2 步行路径规划

**服务地址**: `https://restapi.amap.com/v5/direction/walking` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **origin** | 起点经纬度 | 经度,纬度，小数点不超过6位 | 是 | 无 |
| **destination** | 目的地经纬度 | 经度,纬度，小数点不超过6位 | 是 | 无 |
| isindoor | 室内算路标志 | 0:不需要, 1:需要 | 否 | 0 |
| alternative_route | 返回路线条数 | 1:第一条, 2:前两条, 3:前三条 | 否 | 1 |
| show_fields | 返回结果控制 | 筛选可选字段(如 cost, navi, polyline) | 否 | 空 |
| sig | 数字签名 | 签名校验 | 否 | 无 |
| output | 格式类型 | JSON | 否 | json |

### 1.3 公交路径规划

**服务地址**: `https://restapi.amap.com/v5/direction/transit/integrated` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **origin** | 起点经纬度 | 经度,纬度 | 是 | 无 |
| **destination** | 目的地经纬度 | 经度,纬度 | 是 | 无 |
| **city1** | 起点城市编码 | 仅支持 citycode | 是 | 无 |
| **city2** | 目的地城市编码 | 仅支持 citycode | 是 | 无 |
| strategy | 换乘策略 | 0:推荐, 1:最经济, 2:最少换乘, 3:最少步行, 4:最舒适, 5:不乘地铁等 | 否 | 0 |
| AlternativeRoute | 返回方案条数 | 可传 1-10 的数字 | 否 | 5 |
| date / time | 出发日期/时间 | 日期: 2013-10-28, 时间: 9-54 | 否 | 空 |
| nightflag | 考虑夜班车 | 0:不考虑, 1:考虑 | 否 | 0 |
| show_fields | 返回结果控制 | 筛选可选字段(如 cost, navi, polyline) | 否 | 空 |

---

## 2. 路径规划 1.0 (V3/V4 接口)

### 2.1 距离测量 (Distance V3)

**服务地址**: `https://restapi.amap.com/v3/distance` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **origins** | 出发点列表 | 最多100个坐标对，用"\|"分隔 | 是 | 无 |
| **destination** | 目的地 | 规则同起点 | 是 | 无 |
| type | 路径计算方式 | 0:直线距离, 1:驾车导航距离, 3:步行规划距离(5km内) | 否 | 1 |
| output | 返回格式 | JSON, XML | 否 | JSON |

### 2.2 骑行路径规划 (V4)

**服务地址**: `https://restapi.amap.com/v4/direction/bicycling` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **origin** | 出发点经纬度 | 经度,纬度 | 是 | 无 |
| **destination** | 目的地经纬度 | 经度,纬度 | 是 | 无 |

---

## 3. 地点搜索 2.0 (POI Search V5)

### 3.1 关键字搜索

**服务地址**: `https://restapi.amap.com/v5/place/text` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **keywords** | 地点关键字 | 检索文本，不超过80字符 (与 types 二选一必填) | 部分 | 无 |
| **types** | 地点类型 | POI 分类码，多个用"\|"分隔 (与 keywords 二选一必填) | 部分 | 无 |
| region | 搜索区划 | 城市名、citycode 或 adcode | 否 | 全国 |
| city_limit | 城市召回限制 | true: 仅召回 region 内数据, false: 不限制 | 否 | false |
| page_size | 分页条数 | 取值 1-25 | 否 | 10 |
| page_num | 当前页码 | 请求第几页 | 否 | 1 |
| show_fields | 返回字段控制 | children, business, indoor, navi, photos | 否 | 基础信息 |

### 3.2 周边搜索

**服务地址**: `https://restapi.amap.com/v5/place/around` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **location** | 中心点坐标 | 经度,纬度 | 是 | 无 |
| keywords / types | 关键字/类型 | 规则同关键字搜索 | 否 | 05/07/120000 |
| radius | 搜索半径 | 0-50000 米 | 否 | 5000 |
| sortrule | 排序规则 | distance: 按距离, weight: 综合排序 | 否 | distance |

### 3.3 输入提示 (V3)

**服务地址**: `https://restapi.amap.com/v3/assistant/inputtips` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **keywords** | 查询关键词 | 用户输入内容 | 是 | 无 |
| type | POI 分类 | 强烈建议使用分类代码 | 否 | 无 |
| location | 优先返回坐标 | 在此坐标附近优先返回 | 否 | 无 |
| city | 搜索城市 | citycode 或 adcode | 否 | 无 |
| citylimit | 仅返回指定城市 | true / false | 否 | false |
| datatype | 返回数据类型 | all, poi, bus, busline | 否 | all |

---

## 4. 地图展示 (Static Maps V3)

**服务地址**: `https://restapi.amap.com/v3/staticmap` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **location** | 中心点 | 中心点坐标，若有 markers/paths 则选填 | 条件必填 | 无 |
| **zoom** | 地图级别 | [1, 17] | 条件必填 | 无 |
| size | 地图大小 | 宽*高，最大 1024*1024 | 否 | 400*400 |
| scale | 高清图 | 1:普通, 2:高清(高度宽度zoom均翻倍) | 否 | 1 |
| markers | 标注 | 样式:经纬度;经纬度...\|样式2:经纬度... | 否 | 无 |
| labels | 标签 | 样式:经纬度;经纬度... | 否 | 无 |
| paths | 折线/多边形 | 样式:经纬度;经纬度... | 否 | 无 |
| traffic | 交通路况 | 0:不展现, 1:展现实时路况 | 否 | 0 |

---

## 5. 坐标转换 (Coordinate Convert V3)

**服务地址**: `https://restapi.amap.com/v3/assistant/coordinate/convert` (GET)

| 参数名 | 含义 | 规则说明 | 是否必填 | 缺省值 |
| :--- | :--- | :--- | :--- | :--- |
| **key** | 高德Key | 用户申请的 Key | 是 | 无 |
| **locations** | 待转换坐标 | 经度,纬度，多个用"\|"分割，最多40对 | 是 | 无 |
| coordsys | 原坐标系 | gps, mapbar, baidu, autonavi(不转换) | 否 | autonavi |
| output | 返回格式 | JSON, XML | 否 | JSON |

---

## 附录：通用错误处理与安全

- **状态判断**: 检查返回 JSON 中的 `status` (1:成功, 0:失败)。
- **错误码**: 若失败，查看 `infocode` 和 `info`。常见如 10001 (key不正确)。
- **安全校验**: 若在控制台开启了数字签名，需在请求中加入 `sig` 参数。
- **并发控制**: 不同的开发者 Key 有不同的并发和日配额限制。
