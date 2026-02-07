/**
 * Formatting utility functions.
 */

/** Get transport icon class for a given transport type */
export function getTransportIcon(type) {
  const icons = {
    driving: 'fa-car',
    transit: 'fa-bus',
    walking: 'fa-walking',
    cycling: 'fa-bicycle',
    flight: 'fa-plane',
    train: 'fa-train',
  }
  return icons[type] || 'fa-car'
}

/** Get transport label for a given segment */
export function getTransportLabel(segment) {
  if (!segment) return '驾车'
  const labels = {
    driving: '驾车',
    transit: (segment.details?.display_label === '城际交通') ? '城际交通' : '公交',
    walking: '步行',
    cycling: '骑行',
    flight: segment.details?.flight_no || '航班',
    train: segment.details?.train_no || '高铁',
  }
  return labels[segment.type] || '驾车'
}

/** City data for autocomplete */
export const CITY_DATA = {
  "热门": ["北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "重庆", "武汉", "南京"],
  "直辖市": ["北京", "天津", "上海", "重庆"],
  "广东省": ["广州", "深圳", "珠海", "汕头", "佛山", "韶关", "湛江", "肇庆", "江门", "茂名", "惠州", "梅州", "汕尾", "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮"],
  "浙江省": ["杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水"],
  "江苏省": ["南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁"],
  "四川省": ["成都", "自贡", "攀枝花", "泸州", "德阳", "绵阳", "广元", "遂宁", "内江", "乐山", "南充", "眉山", "宜宾", "广安", "达州", "雅安", "巴中", "资阳", "阿坝", "甘孜", "凉山"],
}
