<script setup>
import { ref } from 'vue'

const activeTab = ref('go') // 'go' or 'back' for commute section
</script>

<template>
  <div class="min-h-screen pb-20 pt-20" style="background: var(--bg-page);">
    <div class="container mx-auto px-4 max-w-4xl">
      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold mb-2" style="color: var(--text-heading);">深圳荟语酒店 ⇄ 香港两日游</h1>
        <p class="text-lg" style="color: var(--text-secondary);">完整攻略 & 行程规划</p>
      </div>

      <!-- Hotel Info -->
      <section class="mb-8 rounded-xl p-6 shadow-sm transition-shadow hover:shadow-md" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <h2 class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
          <span class="text-2xl">🏨</span> 酒店信息
        </h2>
        <div class="space-y-3" style="color: var(--text-primary);">
          <h3 class="font-semibold text-lg">荟语酒店（深圳福田口岸会展中心店）</h3>
          <ul class="list-disc list-inside space-y-2 ml-2">
            <li><span class="font-medium">地址：</span>福民路199号（石厦地铁站E口步行250米）</li>
            <li><span class="font-medium">评分：</span>4.7分</li>
            <li><span class="font-medium">地铁：</span>石厦站（10号线坂田线 / 3号线龙岗线）</li>
            <li><span class="font-medium">福田口岸：</span>地铁10号线仅1站，或步行约30分钟（2.2km）</li>
          </ul>
        </div>
      </section>

      <!-- Weather -->
      <section class="mb-8 rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <h2 class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
          <span class="text-2xl">🌤️</span> 天气预报
        </h2>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-color);">
                <th class="p-3 font-semibold" style="color: var(--text-secondary);">日期</th>
                <th class="p-3 font-semibold" style="color: var(--text-secondary);">白天</th>
                <th class="p-3 font-semibold" style="color: var(--text-secondary);">夜间</th>
                <th class="p-3 font-semibold" style="color: var(--text-secondary);">气温</th>
              </tr>
            </thead>
            <tbody style="color: var(--text-primary);">
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <td class="p-3">2/12 周四</td>
                <td class="p-3">多云</td>
                <td class="p-3">晴</td>
                <td class="p-3">16~24°C</td>
              </tr>
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <td class="p-3">2/13 周五</td>
                <td class="p-3">晴</td>
                <td class="p-3">晴</td>
                <td class="p-3">17~25°C</td>
              </tr>
              <tr>
                <td class="p-3">2/14 周六</td>
                <td class="p-3">晴</td>
                <td class="p-3">晴</td>
                <td class="p-3">18~27°C</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="mt-4 p-3 rounded-lg flex gap-3" style="background: var(--bg-inset); color: var(--text-secondary);">
          <svg class="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <p>天气不错，适合出行！建议穿长袖+薄外套，早晚稍凉。</p>
        </div>
      </section>

      <!-- Commute -->
      <section class="mb-8 rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <h2 class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
          <span class="text-2xl">🚇</span> 每日通勤
        </h2>
        
        <div class="flex space-x-1 mb-6 p-1 rounded-lg" style="background: var(--bg-input);">
          <button 
            @click="activeTab = 'go'"
            class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200"
            :style="activeTab === 'go' ? 'background: var(--bg-card); color: var(--text-heading); box-shadow: var(--card-shadow);' : 'color: var(--text-muted);'"
          >
            去程 (酒店 → 香港)
          </button>
          <button 
            @click="activeTab = 'back'"
            class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200"
            :style="activeTab === 'back' ? 'background: var(--bg-card); color: var(--text-heading); box-shadow: var(--card-shadow);' : 'color: var(--text-muted);'"
          >
            回程 (香港 → 酒店)
          </button>
        </div>

        <div v-if="activeTab === 'go'" class="space-y-6">
          <div class="relative pl-6 border-l-2" style="border-color: var(--border-color);">
            <div class="mb-6 ml-4">
              <span class="absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 bg-white" style="border-color: var(--nav-active-text);"></span>
              <h3 class="font-bold text-lg mb-2" style="color: var(--text-heading);">1. 酒店 → 福田口岸</h3>
              <p class="mb-2" style="color: var(--text-primary);">推荐 <span class="font-bold">7:00</span> 出发</p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-3 rounded-lg" style="background: var(--bg-inset);">
                  <p class="font-semibold" style="color: var(--text-primary);">地铁 (推荐)</p>
                  <p class="text-sm" style="color: var(--text-secondary);">石厦站 → 福田口岸站 (1站)</p>
                  <p class="text-sm mt-1" style="color: var(--text-muted);">约5分钟 | 2元</p>
                </div>
                <div class="p-3 rounded-lg" style="background: var(--bg-inset);">
                  <p class="font-semibold" style="color: var(--text-primary);">步行</p>
                  <p class="text-sm" style="color: var(--text-secondary);">沿福民路向东走</p>
                  <p class="text-sm mt-1" style="color: var(--text-muted);">约30分钟 | 免费</p>
                </div>
              </div>
            </div>

            <div class="mb-6 ml-4">
              <span class="absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 bg-white" style="border-color: var(--nav-active-text);"></span>
              <h3 class="font-bold text-lg mb-2" style="color: var(--text-heading);">2. 福田口岸过关</h3>
              <ul class="list-disc list-inside space-y-1 text-sm" style="color: var(--text-secondary);">
                <li>开放时间：6:30 ~ 22:30</li>
                <li>材料：港澳通行证</li>
                <li>耗时：非高峰约15~20分钟</li>
              </ul>
            </div>

            <div class="ml-4">
              <span class="absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 bg-white" style="border-color: var(--nav-active-text);"></span>
              <h3 class="font-bold text-lg mb-2" style="color: var(--text-heading);">3. 进入香港</h3>
              <div class="p-4 rounded-lg border-l-4" style="background: var(--bg-inset); border-color: var(--nav-active-text);">
                <p class="font-bold mb-2" style="color: var(--text-heading);">推荐方案：港铁</p>
                <p class="text-sm mb-2" style="color: var(--text-primary);">落马洲 → 东铁线直达旺角/尖沙咀</p>
                <p class="text-sm" style="color: var(--text-secondary);">约37分钟 | ~45港币 | 支付宝/微信扫码</p>
              </div>
              <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div class="p-3 rounded border" style="border-color: var(--border-color);">
                  <p class="font-semibold" style="color: var(--text-primary);">大巴 (最省钱)</p>
                  <p class="text-xs mt-1" style="color: var(--text-muted);">B1巴士 → 268X (需同一支付方式换乘) | ~14.86港币</p>
                </div>
                <div class="p-3 rounded border" style="border-color: var(--border-color);">
                  <p class="font-semibold" style="color: var(--text-primary);">高铁 (最快)</p>
                  <p class="text-xs mt-1" style="color: var(--text-muted);">福田 → 西九龙 | 14分钟 | 68元</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="space-y-6">
          <div class="p-4 rounded-lg mb-6 flex items-start gap-3" style="background: rgba(239, 68, 68, 0.1); color: #B91C1C;">
            <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <div>
              <p class="font-bold">务必在 21:30 前从香港出发</p>
              <p class="text-sm opacity-90">需确保 22:30 前完成福田口岸通关</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 rounded-lg" style="background: var(--bg-inset);">
              <h3 class="font-bold mb-2" style="color: var(--text-heading);">港铁回程</h3>
              <p class="text-sm mb-2" style="color: var(--text-primary);">各站 → 落马洲站</p>
              <p class="text-xs font-semibold" style="color: var(--nav-active-text);">建议 21:00 前上车</p>
            </div>
            <div class="p-4 rounded-lg" style="background: var(--bg-inset);">
              <h3 class="font-bold mb-2" style="color: var(--text-heading);">大巴回程</h3>
              <p class="text-sm mb-2" style="color: var(--text-primary);">旺角 → 268X → B1</p>
              <p class="text-xs font-semibold" style="color: var(--nav-active-text);">建议 20:30 前出发</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Day 1 -->
      <section class="mb-8 rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <h2 class="text-xl font-bold mb-6 flex items-center gap-2" style="color: var(--text-heading);">
          <span class="text-2xl">🏙️</span> Day 1：九龙半岛经典游
        </h2>
        
        <div class="relative border-l-2 ml-3 space-y-8" style="border-color: var(--border-subtle);">
          <!-- Item -->
          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">08:10</span>
              <span class="font-semibold" style="color: var(--text-primary);">早餐：华嫂冰室</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">推荐菠萝包+冻奶茶，人均75港币</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">09:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">星光大道 + 维港日景</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">海滨长廊漫步，拍照打卡</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">10:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">天星小轮 (尖沙咀→中环)</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">体验维港风光，约4港币</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">11:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">中环街市 + 半山扶梯</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">全球最长户外有盖自动扶梯</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">12:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">午餐</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">推荐一澜拉面（超浓汤+5倍辣）</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">13:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">香港摩天轮</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">中环民光街，约20港币</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">15:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">旺角逛街</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">女人街、波鞋街、花园街</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">18:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">维港夜景</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">回尖沙咀看夜景，20:00返程</p>
          </div>
        </div>
      </section>

      <!-- Day 2 -->
      <section class="mb-8 rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <h2 class="text-xl font-bold mb-6 flex items-center gap-2" style="color: var(--text-heading);">
          <span class="text-2xl">🚋</span> Day 2：港岛深度游
        </h2>
        
        <div class="relative border-l-2 ml-3 space-y-8" style="border-color: var(--border-subtle);">
          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">08:10</span>
              <span class="font-semibold" style="color: var(--text-primary);">Bakehouse早餐</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">推荐肉桂卷、燕麦曲奇</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">09:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">山顶缆车上太平山</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">建议早上去排队少，单程约52港币</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">11:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">15号巴士下山</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">到中环，比缆车快且便宜</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">11:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">叮叮车体验</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">中环 → 坚尼地城，2.6港币，体验慢节奏</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">12:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">坚尼地城 + 午餐</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">网红篮球场、海边打卡</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">14:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">PMQ元创方 / 涂鸦墙</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">中环荷李活道，文艺打卡</p>
          </div>

          <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">15:30</span>
              <span class="font-semibold" style="color: var(--text-primary);">铜锣湾购物</span>
            </div>
            <p class="text-sm" style="color: var(--text-secondary);">时代广场、SOGO</p>
          </div>
          
           <div class="relative pl-8">
            <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
              <span class="font-bold text-lg" style="color: var(--text-heading);">20:00</span>
              <span class="font-semibold" style="color: var(--text-primary);">返程</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Tips & Cost -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section class="rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
          <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
            <span class="text-xl">💳</span> 支付方式
          </h2>
          <ul class="space-y-3 text-sm" style="color: var(--text-primary);">
            <li class="flex items-start gap-2">
              <span class="text-blue-500">•</span>
              <span><strong>港铁/巴士：</strong>支付宝/微信乘车码 (巴士需同一种方式享优惠)</span>
            </li>
             <li class="flex items-start gap-2">
              <span class="text-blue-500">•</span>
              <span><strong>小轮/叮叮车：</strong>支付宝/八达通</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-blue-500">•</span>
              <span><strong>消费：</strong>大部分支持支付宝/微信，建议备少量现金(200港币)</span>
            </li>
          </ul>
        </section>

        <section class="rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
          <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
            <span class="text-xl">💰</span> 费用估算 (每人)
          </h2>
          <div class="space-y-3 text-sm" style="color: var(--text-primary);">
            <div class="flex justify-between border-b pb-2" style="border-color: var(--border-subtle);">
              <span>交通</span>
              <span class="font-mono">~250-300 HKD</span>
            </div>
            <div class="flex justify-between border-b pb-2" style="border-color: var(--border-subtle);">
              <span>餐饮</span>
              <span class="font-mono">~600-1000 HKD</span>
            </div>
            <div class="flex justify-between border-b pb-2" style="border-color: var(--border-subtle);">
              <span>景点</span>
              <span class="font-mono">~150 HKD</span>
            </div>
            <div class="flex justify-between pt-1 font-bold text-lg" style="color: var(--nav-active-text);">
              <span>总计</span>
              <span>~1000-1500 HKD</span>
            </div>
          </div>
        </section>
      </div>
      
       <div class="mt-8 text-center">
         <a href="amapuri://workInAmap/createWithToken?polymericId=mcp_c09e986be318461c9b4f327a2babfd5b&from=MCP" target="_blank" class="inline-flex items-center gap-2 px-6 py-3 rounded-full font-bold text-white shadow-lg transition-transform hover:scale-105 active:scale-95" style="background: linear-gradient(135deg, var(--logo-text-from), var(--logo-text-to));">
           <span>🗺️ 打开高德地图行程</span>
         </a>
       </div>

    </div>
  </div>
</template>
